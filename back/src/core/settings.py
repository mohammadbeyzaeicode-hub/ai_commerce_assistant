import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv


# مسیر .env (روت پروژه)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / ".env"

# بارگذاری .env
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings(BaseModel):
    #OpenAi
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # GAPGPT
    GAPGPT_API_KEY: str = os.getenv("GAPGPT_API_KEY", "")
    GAPGPT_BASE_URL: str = os.getenv("GAPGPT_BASE_URL", "")
    model: str = os.getenv("model", "")
    
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    MINI_APP_URL: str = os.getenv("MINI_APP_URL", "")

    # اختیاری
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # مسیرهای داخلی پروژه
    # BASE_DIR: str = str(BASE_DIR)
    PROMPT_PATH: str = str(BASE_DIR / "ai" / "prompts" / "system_prompt.txt")

    SELLER_IDS: list[int] =os.getenv("SELLER_IDS", [])

# Singleton
settings = Settings()
