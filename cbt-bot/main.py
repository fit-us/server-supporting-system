# filepath: c:\fit-us\supporting\cbt-bot-py\cbt_bot.py
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from markdown_utils import MarkdownReader
from config import Config
import json

@dataclass
class CBTBot:
    llm: ChatGoogleGenerativeAI
    prompt: str

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_OUTPUT_TOKENS,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.prompt = MarkdownReader.read_file(Config.PROMPT_PATH)

    def invoke(self, message):
        return self.llm.invoke([
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": message},
        ])
    
def preprocess_response(response_content):
    # ```json 태그를 제거하고 JSON 데이터만 추출
    if response_content.startswith("```json"):
        response_content = response_content[7:]
    if response_content.endswith("```"):
        response_content = response_content[:-3]
    return response_content.strip()

if __name__ == "__main__":
    bot = CBTBot()
    # print(bot.prompt)
    # 예제 메시지
    response = bot.invoke("나 오늘 회사에서 말을 실수해서 우울해")
    
    # # response가 AIMessage 객체인 경우 content 속성에서 텍스트 추출
    response_content = response.content if hasattr(response, 'content') else str(response)
    processed_response = preprocess_response(response_content)
    # # print("Processed Response:", processed_response)

    # # JSON 데이터로 변환
    try:
        json_data = json.loads(processed_response)
        # json.dumps(json_data, indent=4, ensure_ascii=False)
        
        # JSON 객체의 키 출력
        print("JSON Keys:")
        print(json_data['therapistNotes'])
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류: {e}")