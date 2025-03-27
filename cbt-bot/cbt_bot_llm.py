import pickle
import asyncio
import redis
import logging
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from utils.markdown_utils import MarkdownReader
from config import LLM,REDIS
from utils.json_serializer import JsonSerializer
from cbt_bot_model import AnalysisResponse,CBTResponse

class CBTBotLLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=LLM.MODEL,
            temperature=LLM.TEMPERATURE,
            max_output_tokens=LLM.MAX_OUTPUT_TOKENS,
            google_api_key=LLM.GOOGLE_API_KEY,
        )
        self.prompts = {
            "consultation": MarkdownReader.read_file(LLM.CONSULTATION_PROMPT_PATH),
            "cbt": MarkdownReader.read_file(LLM.CBT_PROMPT_PATH),
            "analysis": MarkdownReader.read_file(LLM.ANALYSIS_PROMPT_PATH),
        }
        self.user_memories_prefix = "user_memory:"

        # ✅ Redis 연결 확인
        try:
            self.redis_client = redis.Redis(host=REDIS.HOST, port=REDIS.PORT, db=REDIS.DB)
            self.redis_client.ping()  # Redis 서버가 응답하는지 확인
            logging.info("✅ Redis 연결 성공!")
        except redis.ConnectionError as e:
            logging.error(f"❌ Redis 연결 실패: {e}")
            raise

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """Redis에서 사용자 메모리를 가져옴"""
        memory_key = f"{self.user_memories_prefix}{user_id}"
        memory_data = self.redis_client.get(memory_key)

        if memory_data:
            try:
                memory = pickle.loads(memory_data)  # 🔹 역직렬화
                return memory
            except pickle.PickleError as e:
                logging.error(f"❌ Redis 데이터 역직렬화 실패: {e}")
            except Exception as e:
                logging.error(f"❌ 예상치 못한 오류: {e}")

        logging.warning(f"⚠️ 사용자 {user_id}의 대화 기록 없음. 새로운 메모리 생성.")
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def save_memory(self, user_id: str, memory: ConversationBufferMemory):
        """메모리를 Redis에 저장"""
        try:
            memory_data = pickle.dumps(memory)  # 🔹 직렬화
            self.redis_client.set(f"{self.user_memories_prefix}{user_id}", memory_data)
            logging.info(f"✅ 사용자 {user_id}의 대화 기록 저장 성공.")
        except Exception as e:
            logging.error(f"❌ 대화 기록 저장 실패: {e}")

    async def invoke_stream(self, user_id: str, message: str):
        """ 각 프롬프트(consultation, cbt, analysis)를 병렬 실행하여 응답을 스트리밍 반환 """
        try:
            tasks = {
                "consultation": self.invoke(user_id, self.prompts["consultation"], message),
                "cbt": self.invoke(user_id, self.prompts["cbt"], message),
                "analysis": self.invoke(user_id, self.prompts["analysis"], message),
            }
            logging.info(f"Tasks 생성됨: {tasks}")  # 디버깅 로그 추가

            # 🔹 병렬 실행
            for prompt_type, task in tasks.items():
                logging.info(f"Task 실행 시작: {prompt_type}")
                result = ""
                async for chunk in task: 
                    if prompt_type == "consultation":
                        yield (prompt_type, chunk)
                        await asyncio.sleep(0)  # 0.2초 간격으로 출력
                    else:
                        result += chunk
                if prompt_type == "cbt":
                    yield (prompt_type, JsonSerializer.from_json(CBTResponse,result))
                elif prompt_type == "analysis":
                    yield (prompt_type, JsonSerializer.from_json(AnalysisResponse,result))
        except Exception as e:
            logging.error(f"invoke_stream 처리 중 오류 발생: {e}")
            raise

    async def invoke(self, user_id: str, prompt:str, message: str):
        """사용자 메시지를 받아 LLM을 호출하고 응답을 반환"""
        memory_key = f"{self.user_memories_prefix}{user_id}"
        
        # Redis 트랜잭션 시작
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    # Redis에서 사용자 메모리 가져오기
                    pipe.watch(memory_key)
                    memory_data = pipe.get(memory_key)

                    if memory_data:
                        memory = pickle.loads(memory_data)  # 🔹 역직렬화
                    else:
                        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

                    # 기억된 대화를 포함하여 모델에 전달
                    messages = [SystemMessage(content=prompt, role="system")]
                    messages.extend([AIMessage(content=m.content, role=m.type) for m in memory.chat_memory.messages])
                    messages.append(HumanMessage(content=message, role="user"))

                    response = ""
                    try:
                        async for chunk in self.llm.astream(messages):
                            response += chunk.content
                            yield chunk.content  # 🔹 스트리밍 반환
                    except Exception as e:
                        logging.error(f"LLM 호출 중 오류 발생: {e}")
                    
                    memory.save_context({"input": message}, {"output": response})
                    memory_data = pickle.dumps(memory)  # 🔹 직렬화

                    # Redis 트랜잭션 실행
                    pipe.multi()
                    pipe.set(memory_key, memory_data)
                    pipe.execute()
                    logging.info(f"✅ 사용자 {user_id}의 대화 기록 업데이트 성공.")
                    break
                except redis.WatchError:
                #     # 다른 클라이언트가 메모리를 수정한 경우 재시도
                    logging.warning(f"⚠️ 사용자 {user_id}의 대화 기록 업데이트 충돌. 재시도 중...")
                    continue