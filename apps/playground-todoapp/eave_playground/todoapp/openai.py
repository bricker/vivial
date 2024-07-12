from openai import AsyncOpenAI

from .secrets import get_secret


async def chat_completion(prompt: str) -> str | None:
    openai_client = AsyncOpenAI(
        api_key=get_secret("OPENAI_API_KEY"),
    )

    chat_completion = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    return chat_completion.choices[0].message.content
