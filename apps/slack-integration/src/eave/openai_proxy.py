import enum
import logging
from typing import Optional

import openai
from openai.openai_object import OpenAIObject

from eave.settings import APP_SETTINGS


class OpenAIModel(enum.Enum):
    ADA = "text-ada-001"
    ADA_EMBEDDING = "text-embedding-ada-002"
    CURIE = "text-curie-001"
    BABBAGE = "text-babbage-001"
    DAVINCI = "text-davinci-003"


async def summarize(prompt: str, temperature: int = 0, max_tokens: int = 2048) -> Optional[str]:
    """
    https://beta.openai.com/docs/api-reference/completions/create
    other parameters to consider:
    - presence_penalty
    - frequency_penalty
    - top_p
    """

    # Set this here so that the openai key is pulled from GCP Secrets Manager lazily
    if openai.api_key is None:
        openai.api_key = APP_SETTINGS.eave_openapi_key

    response = openai.Completion.create(
        model=OpenAIModel.DAVINCI.value,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if isinstance(response, OpenAIObject):
        logging.info("openAI response payload:", extra={"json_fields": {"response": response}})
        cleaned_answer = str(response.choices[0].text).strip()
        return cleaned_answer
    else:
        logging.warning("unexpected response from OpenAI")
        return None


# def get_embedding(text, model=OpenAIModel.ADA_EMBEDDING):
#     text = text.replace("\n", " ")
#     return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


# df = pandas.read_csv("output/embedded_1k_reviews.csv")
# df["ada_embedding"] = df.ada_embedding.apply(eval).apply(numpy.array)
# df["ada_embedding"] = df.combined.apply(lambda x: get_embedding(x, model=OpenAIModel.ADA_EMBEDDING))
# df.to_csv("output/embedded_1k_reviews.csv", index=False)
