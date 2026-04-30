from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from app.core.config import settings

# ✅ Safe initialization
if settings.OPENAI_API_KEY:
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=0.2,
        timeout=30
    )
else:
    Settings.llm = None
    print("⚠️ OPENAI_API_KEY not set — QA will not work")
