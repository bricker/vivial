from decimal import Decimal
import enum
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

_MILLION = Decimal("1e6")
_SIXTY = Decimal("60")

class OpenAIModelPricingStructure(enum.Enum):
    PER_TOKEN_BY_TYPE = enum.auto()
    PER_TOKEN = enum.auto()
    PER_AUDIO_DURATION_MINUTE = enum.auto()
    PER_IMAGE = enum.auto()
    PER_CHAR = enum.auto()
    FREE = enum.auto()
    UNKNOWN = enum.auto()


@dataclass(kw_only=True, frozen=True)
class OpenAIModel(ABC):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.UNKNOWN


@dataclass(kw_only=True, frozen=True)
class OpenAITokenModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_TOKEN_BY_TYPE

    usd_cents_per_million_input_tokens: Decimal
    usd_cents_per_million_output_tokens: Decimal

    def calculate_input_cost_usd_cents(self, *, prompt_tokens: int) -> Decimal:
        return (self.usd_cents_per_million_input_tokens / _MILLION) * Decimal(str(prompt_tokens))

    def calculate_output_cost_usd_cents(self, *, completion_tokens: int) -> Decimal:
        return (self.usd_cents_per_million_output_tokens / _MILLION) * Decimal(str(completion_tokens))


@dataclass(kw_only=True, frozen=True)
class OpenAIEmbeddingModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_TOKEN

    usd_cents_per_million_tokens: Decimal

    def calculate_total_cost_usd_cents(self, *, total_tokens: int) -> Decimal:
        return (self.usd_cents_per_million_tokens / _MILLION) * Decimal(str(total_tokens))


# @dataclass(kw_only=True, frozen=True)
# class OpenAIFineTuningModel(OpenAIModel):
#     pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_TOKEN_BY_TYPE

#     usd_cents_per_million_input_tokens: float
#     usd_cents_per_million_output_tokens: float
#     usd_cents_per_million_training_tokens: float

#     @property
#     def usd_cents_per_input_token(self) -> float:
#         return self.usd_cents_per_million_input_tokens / 1e6

#     @property
#     def usd_cents_per_output_token(self) -> float:
#         return self.usd_cents_per_million_output_tokens / 1e6

#     @property
#     def usd_cents_per_training_token(self) -> float:
#         return self.usd_cents_per_million_training_tokens / 1e6

#     def calculate_total_cost_usd_cents(self, *, prompt_tokens: int, completion_tokens: int) -> float:
#         return self.usd_cents_per_token * total_tokens


@dataclass(kw_only=True, frozen=True)
class OpenAIImageModelResolution(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_IMAGE

    usd_cents_per_image: Decimal

    def calculate_total_cost_usd_cents(self) -> Decimal:
        return self.usd_cents_per_image


@dataclass(kw_only=True, frozen=True)
class OpenAITextToSpeechModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_CHAR

    usd_cents_per_million_chars: Decimal

    def calculate_total_cost_usd_cents(self, *, num_chars: int) -> Decimal:
        return (self.usd_cents_per_million_chars / _MILLION) * Decimal(str(num_chars))


@dataclass(kw_only=True, frozen=True)
class OpenAITranscriptionModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_AUDIO_DURATION_MINUTE

    usd_cents_per_input_minute: Decimal

    def calculate_total_cost_usd_cents(self, *, input_duration_seconds: float) -> Decimal:
        # Note that OpenAI rounds the duration to the nearest second when calculating price.
        return (self.usd_cents_per_input_minute / _SIXTY) * Decimal(str(round(input_duration_seconds)))


@dataclass(kw_only=True, frozen=True)
class OpenAIModerationModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.FREE

    def calculate_total_cost_usd_cents(self) -> Decimal:
        # it's free!
        return Decimal("0")


# fmt: off

# The floats here are formatted so that they visually match the OpenAI Pricing page.
# The pricing page by default lists prices per million "things", eg input tokens or characters, in US Dollars.
# By formatting these as X.XX, they can be quickly verified visually against the pricing page.
# But, we do the math and store these (in BQ) as USD _cents_, which is why we multiply by 100 (e2).
CHAT_MODELS = {
    "gpt-4o":                       OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("5.00e2"),  usd_cents_per_million_output_tokens=Decimal("15.00e2")),
    "gpt-4o-2024-05-13":            OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("5.00e2"),  usd_cents_per_million_output_tokens=Decimal("15.00e2")),
    "gpt-4-turbo":                  OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4-turbo-2024-04-09":       OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4-turbo-preview":          OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4":                        OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("30.00e2"), usd_cents_per_million_output_tokens=Decimal("60.00e2")),
    "gpt-4-0613":                   OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("30.00e2"), usd_cents_per_million_output_tokens=Decimal("60.00e2")),
    "gpt-4-0125-preview":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4-1106-preview":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4-vision-preview":         OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("10.00e2"), usd_cents_per_million_output_tokens=Decimal("30.00e2")),
    "gpt-4-32k":                    OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("60.00e2"), usd_cents_per_million_output_tokens=Decimal("120.00e2")),
    "gpt-3.5-turbo":                OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("0.50e2"),  usd_cents_per_million_output_tokens=Decimal("1.50e2")),
    "gpt-3.5-turbo-0125":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("0.50e2"),  usd_cents_per_million_output_tokens=Decimal("1.50e2")),
    "gpt-3.5-turbo-1106":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.00e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "gpt-3.5-turbo-0613":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.50e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "gpt-3.5-turbo-0301":           OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.50e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "gpt-3.5-turbo-16k":            OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("3.00e2"),  usd_cents_per_million_output_tokens=Decimal("4.00e2")),
    "gpt-3.5-turbo-16k-0613":       OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("3.00e2"),  usd_cents_per_million_output_tokens=Decimal("4.00e2")),
    "gpt-3.5-turbo-instruct":       OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.50e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "gpt-3.5-turbo-instruct-0914":  OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.50e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "davinci-002":                  OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("2.00e2"),  usd_cents_per_million_output_tokens=Decimal("2.00e2")),
    "babbage-002":                  OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("0.40e2"),  usd_cents_per_million_output_tokens=Decimal("0.40e2")),
}

FINE_TUNING_MODELS = {
    "gpt-3.5-turbo":    OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("3.00e2"),  usd_cents_per_million_output_tokens=Decimal("6.00e2")),
    "davinci-002":      OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("12.00e2"), usd_cents_per_million_output_tokens=Decimal("12.00e2")),
    "babbage-002":      OpenAITokenModel(usd_cents_per_million_input_tokens=Decimal("1.60e2"),  usd_cents_per_million_output_tokens=Decimal("1.60e2")),
}

# dall-e-2 is the default if not specified when generating an image.
DALLE_2_MODELS = {
    "256x256":      OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.016e2")),
    "512x512":      OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.018e2")),
    "1024x1024":    OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.020e2")), # default
}

# Only dall-e-3 has a resolution ("standard" or "hd") response value.
DALLE_3_MODELS = {
    "standard": { # default
        "1024x1024": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.04e2")), # default
        "1792x1024": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.08e2")),
        "1024x1792": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.08e2")),
    },
    "hd": {
        "1024x1024": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.08e2")), # default
        "1792x1024": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.12e2")),
        "1024x1792": OpenAIImageModelResolution(usd_cents_per_image=Decimal("0.12e2")),
    },
}

EMBEDDING_MODELS = {
    # Embedding Models
    "text-embedding-3-small": OpenAIEmbeddingModel(usd_cents_per_million_tokens=Decimal("0.02e2")),
    "text-embedding-3-large": OpenAIEmbeddingModel(usd_cents_per_million_tokens=Decimal("0.13e2")),
    "text-embedding-ada-002": OpenAIEmbeddingModel(usd_cents_per_million_tokens=Decimal("0.10e2")),
}

TTS_MODELS = {
    # Text-to-speech models
    "tts-1":            OpenAITextToSpeechModel(usd_cents_per_million_chars=Decimal("15.00e2")),
    "tts-1-1106":       OpenAITextToSpeechModel(usd_cents_per_million_chars=Decimal("15.00e2")),
    "tts-1-hd":         OpenAITextToSpeechModel(usd_cents_per_million_chars=Decimal("30.00e2")),
    "tts-1-hd-1106":    OpenAITextToSpeechModel(usd_cents_per_million_chars=Decimal("30.00e2")),
}

TRANSCRIPTION_MODELS = {
    # Transcription models
    "whisper-1": OpenAITranscriptionModel(usd_cents_per_input_minute=Decimal("0.006e2")),
}

MODERATION_MODELS = {
    "text-moderation-latest":   OpenAIModerationModel(),
    "text-moderation-stable":   OpenAIModerationModel(),
    "text-moderation-007":      OpenAIModerationModel(),
}

# fmt: on
