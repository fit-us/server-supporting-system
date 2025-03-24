# filepath: c:\fit-us\supporting\cbt-bot-py\config.py
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.dev")

class Config:
    GOOGLE_API_KEY = os.getenv("GEN_API_KEY")
    MODEL = "gemini-1.5-flash"
    TEMPERATURE = 0
    MAX_OUTPUT_TOKENS = 10000
    PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/system-prompt.md")
