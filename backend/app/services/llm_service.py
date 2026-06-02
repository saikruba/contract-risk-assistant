from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def call_llama(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=1200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert legal contract analyst. "
                    "Answer strictly from the provided contract context. "
                    "If information is missing, say so."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
