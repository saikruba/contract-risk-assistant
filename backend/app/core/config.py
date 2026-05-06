import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Contract Risk Assistant"

    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

settings = Settings()
