from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import dataclass
from markdown_utils import MarkdownReader
from config import Config

@dataclass
class CBTBot:
    llm: ChatGoogleGenerativeAI
    prompt: str
    memory: ConversationBufferMemory

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_OUTPUT_TOKENS,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.prompt = MarkdownReader.read_file(Config.PROMPT_PATH)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def invoke(self, message: str):
        # 기억된 대화를 포함하여 모델에 전달
        messages = [{"role": "system", "content": self.prompt}]
        messages.extend(self.memory.chat_memory.messages)
        messages.append({"role": "user", "content": message})

        response = self.llm.invoke(messages)

        # 대화 내용을 메모리에 저장
        self.memory.save_context({"input": message}, {"output": response.content})

        return response

if __name__ == "__main__":
    bot = CBTBot()

    while True:
        # 사용자로부터 메시지 입력 받기
        user_message = input("사용자: ")
        if user_message.lower() == "exit":  # 사용자가 'exit' 입력 시 종료
            break

        # 봇의 응답 출력
        response = bot.invoke(user_message)
        print(f"봇: {response.content}")