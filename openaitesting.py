import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="sk-proj-jqrV5jXlvyNdtsT3RN3HT3BlbkFJFM1ETraWiCceWrYxK3zU",
)


def chat_completion():
    #
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )

    print(chat_completion)


if __name__ == "__main__":
    chat_completion()