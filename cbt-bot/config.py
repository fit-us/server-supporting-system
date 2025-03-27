# filepath: c:\fit-us\supporting\cbt-bot-py\config.py
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.dev")

class LLM:
    GOOGLE_API_KEY = os.getenv("GEN_API_KEY")
    MODEL = os.getenv("LLM_MODEL")
    TEMPERATURE = os.getenv("LLM_TEMPERATURE")
    MAX_OUTPUT_TOKENS = os.getenv("LLM_MAX_OUTPUT_TOKENS")
    CONSULTATION_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/system-consultation-prompt.md")
    CBT_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/system-cbt-prompt.md")
    ANALYSIS_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/system-analysis-prompt.md")

class REDIS:
    HOST = os.getenv("REDIS_HOST")
    PORT = os.getenv("REDIS_PORT")
    DB = os.getenv("REDIS_DB")