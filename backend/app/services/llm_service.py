from groq import Groq
from app.core.config import settings
from langfuse import get_client
import traceback

# -------------------------------
# Langfuse
# -------------------------------
langfuse = get_client()

# -------------------------------
# Check API Key
# -------------------------------
print("\n========== GROQ CONFIG ==========")

if settings.GROQ_API_KEY:
    print("✓ GROQ_API_KEY Loaded")
    print("Key starts with:", settings.GROQ_API_KEY[:10] + "...")
else:
    print("❌ GROQ_API_KEY NOT FOUND")

print("=================================\n")

# -------------------------------
# Groq Client
# -------------------------------
client = Groq(api_key=settings.GROQ_API_KEY)


# -------------------------------
# LLM Call
# -------------------------------
def call_llama(prompt: str):

    print("\n==============================")
    print("Calling Groq LLM...")
    print("==============================")

    with langfuse.start_as_current_observation(
        as_type="generation",
        name="Groq GPT OSS 120B"
    ) as generation:

        generation.update(
            input=prompt[:3000]
        )

        try:

            response = client.chat.completions.create(

                # CHANGE THIS MODEL IF NEEDED
                model="openai/gpt-oss-120b",

                temperature=0.0,

                max_tokens=1000,

                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal contract assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print("✅ Groq Response Received")

            output = response.choices[0].message.content

            generation.update(
                output=output
            )

            return output

        except Exception as e:

            print("\n")
            print("############################################")
            print("########### GROQ API ERROR #################")
            print("############################################")
            print(type(e))
            print(str(e))
            print("--------------------------------------------")
            traceback.print_exc()
            print("############################################")
            print("\n")

            raise
