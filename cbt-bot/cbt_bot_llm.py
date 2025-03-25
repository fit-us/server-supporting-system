from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from utils.markdown_utils import MarkdownReader
from config import Config
from utils.json_serializer import JsonSerializer
from cbt_bot_model import CBTBotResponse

class CBTBotLLM:
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

        messages = [SystemMessage(content=self.prompt, role="system")]
        messages.extend([AIMessage(content=m.content, role=m.type) for m in self.memory.chat_memory.messages])
        messages.append(HumanMessage(content=message, role="user"))

        response = self.llm.invoke(messages)

        try:
            self.memory.save_context({"input": message}, {"output": response.content})
        except Exception as e:
            print(f"Error saving context: {e}")
        print(response.content)
        return CBTBotResponse(**JsonSerializer.from_json(response.content))