import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "Contract Risk Assistant")
    ENV = os.getenv("ENV", "development")

settings = Settings()
