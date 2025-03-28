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
            "summary": MarkdownReader.read_file(LLM.SUMMARY_PROMPT_PATH),
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

    def save_memory(self, user_id: str, memory: ConversationBufferMemory, max_retries: int = 3):
        memory_key = f"{self.user_memories_prefix}{user_id}"
        retries = 0
        
        while retries < max_retries:
            try:
                memory_data = pickle.dumps(memory)
                with self.redis_client.pipeline() as pipe:
                    pipe.watch(memory_key)
                    pipe.multi()
                    pipe.set(memory_key, memory_data)
                    pipe.execute()
                logging.info(f"✅ 사용자 {user_id}의 대화 기록 저장 성공.")
                return  
            except redis.WatchError:
                retries += 1
                logging.warning(f"⚠️ 사용자 {user_id}의 대화 기록 저장 충돌. 재시도 {retries}/{max_retries}...")
                asyncio.sleep(1)
            except Exception as e:
                logging.error(f"❌ 대화 기록 저장 실패: {e}")
                break 

        # 최대 재시도 횟수를 넘어서면 실패로 처리
        logging.error(f"❌ 사용자 {user_id}의 대화 기록 저장 실패. 재시도 횟수 초과.")

    async def async_invoke(self, messages):
        # invoke가 동기적이라면 이를 비동기적으로 호출하기 위한 래핑
        return await asyncio.to_thread(self.llm.invoke, messages)
    
    async def invoke_stream(self, user_id: str, message: str):
        """ 각 프롬프트(consultation, cbt, analysis)를 병렬 실행하여 응답을 스트리밍 반환 """
        memory_key = f"{self.user_memories_prefix}{user_id}"
        
        try:
            memory_data = self.redis_client.get(memory_key)
            if memory_data:
                memory = pickle.loads(memory_data)  # 🔹 역직렬화
            else:
                memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
            tasks = {
                "consultation": self.invoke(self.prompts["consultation"], message, memory),
                "cbt": self.invoke(self.prompts["cbt"], message, memory),
                "analysis": self.invoke(self.prompts["analysis"], message, memory),
            }
            logging.info(f"Tasks 생성됨: {tasks}")  # 디버깅 로그 추가
            collected_responses = {"consultation": "", "cbt": "", "analysis": "", "summarize":""}  # 응답 모음
            
            
        # 🔹 병렬 실행
            for prompt_type, task in tasks.items():
                logging.info(f"Task 실행 시작: {prompt_type}")
                async for chunk in task:
                    collected_responses[prompt_type] += chunk
                    if prompt_type == "consultation":
                        yield (prompt_type, chunk)
                        await asyncio.sleep(0)

                # CBT와 분석 결과 JSON 변환
                if prompt_type == "cbt":
                    yield (prompt_type, JsonSerializer.from_json(CBTResponse, collected_responses[prompt_type]))
                elif prompt_type == "analysis":
                    yield (prompt_type, JsonSerializer.from_json(AnalysisResponse, collected_responses[prompt_type]))

            async for chunk in self.summarize_result(self.prompts["summary"],collected_responses["consultation"]+collected_responses["cbt"]+collected_responses["analysis"]):
                collected_responses["summarize"] += chunk
            memory.save_context({"input": message}, {"output": collected_responses["summarize"]})
            memory_data = pickle.dumps(memory)  # 🔹 직렬화
            self.save_memory(user_id, memory)
            
            logging.info(f"✅ 사용자 {user_id}의 대화 기록 업데이트 성공.")
        except Exception as e:
            logging.error(f"invoke_stream 처리 중 오류 발생: {e}")
            raise
    async def summarize_result(self, prompt: str,message: str):
        messages = [SystemMessage(content=prompt, role="system")]
        messages.append(HumanMessage(content=message, role="user"))
        try:
            async for chunk in self.llm.astream(messages):
                yield chunk.content  # 🔹 스트리밍 반환
        except Exception as e:
            logging.error(f"LLM 호출 중 오류 발생: {e}")

    async def invoke(self, prompt:str, message: str, memory:ConversationBufferMemory):
        """사용자 메시지를 받아 LLM을 호출하고 응답을 반환"""
        # 기억된 대화를 포함하여 모델에 전달
        messages = [SystemMessage(content=prompt, role="system")]
        messages.extend([AIMessage(content=m.content, role=m.type) for m in memory.chat_memory.messages])
        messages.append(HumanMessage(content=message, role="user"))

        try:
            async for chunk in self.llm.astream(messages):
                yield chunk.content  # 🔹 스트리밍 반환
        except Exception as e:
            logging.error(f"LLM 호출 중 오류 발생: {e}")
        