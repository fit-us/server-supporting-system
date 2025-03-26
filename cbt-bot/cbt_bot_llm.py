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
    user_memories: dict

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_OUTPUT_TOKENS,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.prompt = MarkdownReader.read_file(Config.PROMPT_PATH)
        self.user_memories = {}

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        return self.user_memories[user_id]

    def invoke(self, user_id: str, message: str):
        memory = self.get_memory(user_id)

        # 기억된 대화를 포함하여 모델에 전달
        messages = [SystemMessage(content=self.prompt, role="system")]
        messages.extend([AIMessage(content=m.content, role=m.type) for m in memory.chat_memory.messages])
        messages.append(HumanMessage(content=message, role="user"))

        response = self.llm.invoke(messages)

        try:
            memory.save_context({"input": message}, {"output": response.content})
        except Exception as e:
            print(f"Error saving context: {e}")
        print(response.content)
        return JsonSerializer.from_json(CBTBotResponse, response.content)