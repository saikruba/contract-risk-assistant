from groq import Groq
from app.core.config import settings
from langfuse import get_client

langfuse = get_client()

client = Groq(api_key=settings.GROQ_API_KEY)


def call_llama(prompt: str):

    with langfuse.start_as_current_observation(
        as_type="generation",
        name="Groq Llama"
    ) as generation:

        generation.update(
            input=prompt[:3000]
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=1500,
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

        output = response.choices[0].message.content

        generation.update(
            output=output
        )

        return output
