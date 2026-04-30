import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Contract Risk Assistant"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

settings = Settings()
