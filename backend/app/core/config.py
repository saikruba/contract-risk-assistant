import os
from dotenv import load_dotenv


# Load the .env file
load_dotenv()

class Settings:
    APP_NAME = "Contract Risk Assistant"

    # Langfuse credentials
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

settings = Settings()
