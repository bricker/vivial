import enum
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar


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

    usd_cents_per_million_input_tokens: float
    usd_cents_per_million_output_tokens: float

    @property
    def usd_cents_per_input_token(self) -> float:
        return self.usd_cents_per_million_input_tokens / 1e6

    @property
    def usd_cents_per_output_token(self) -> float:
        return self.usd_cents_per_million_output_tokens / 1e6

    def calculate_input_cost_usd_cents(self, *, prompt_tokens: int) -> float:
        return self.usd_cents_per_input_token * prompt_tokens

    def calculate_output_cost_usd_cents(self, *, completion_tokens: int) -> float:
        return self.usd_cents_per_output_token * completion_tokens


@dataclass(kw_only=True, frozen=True)
class OpenAIEmbeddingModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_TOKEN

    usd_cents_per_million_tokens: float

    @property
    def usd_cents_per_token(self) -> float:
        return self.usd_cents_per_million_tokens / 1e6

    def calculate_total_cost_usd_cents(self, *, total_tokens: int) -> float:
        return self.usd_cents_per_token * total_tokens


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

    usd_cents_per_image: float

    def calculate_total_cost_usd_cents(self) -> float:
        return self.usd_cents_per_image


@dataclass(kw_only=True, frozen=True)
class OpenAITextToSpeechModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_CHAR

    usd_cents_per_million_chars: float

    @property
    def usd_cents_per_char(self) -> float:
        return self.usd_cents_per_million_chars / 1e6

    def calculate_total_cost_usd_cents(self, *, num_chars: int) -> float:
        return self.usd_cents_per_char * num_chars


@dataclass(kw_only=True, frozen=True)
class OpenAITranscriptionModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.PER_AUDIO_DURATION_MINUTE

    usd_cents_per_input_minute: float

    @property
    def usd_cents_per_input_second(self) -> float:
        return self.usd_cents_per_input_minute / 60.0

    def calculate_total_cost_usd_cents(self, *, input_duration_seconds: float) -> float:
        # Note that OpenAI rounds the duration to the nearest second when calculating price.
        return self.usd_cents_per_input_second * round(input_duration_seconds)


@dataclass(kw_only=True, frozen=True)
class OpenAIModerationModel(OpenAIModel):
    pricing_structure: ClassVar[OpenAIModelPricingStructure] = OpenAIModelPricingStructure.FREE

    def calculate_total_cost_usd_cents(self) -> float:
        # it's free!
        return 0


# fmt: off

CHAT_MODELS = {
    "gpt-4o":                       OpenAITokenModel(usd_cents_per_million_input_tokens=5e2,    usd_cents_per_million_output_tokens=15e2),
    "gpt-4o-2024-05-13":            OpenAITokenModel(usd_cents_per_million_input_tokens=5e2,    usd_cents_per_million_output_tokens=15e2),
    "gpt-4-turbo":                  OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4-turbo-2024-04-09":       OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4-turbo-preview":          OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4":                        OpenAITokenModel(usd_cents_per_million_input_tokens=30e2,   usd_cents_per_million_output_tokens=60e2),
    "gpt-4-0613":                   OpenAITokenModel(usd_cents_per_million_input_tokens=30e2,   usd_cents_per_million_output_tokens=60e2),
    "gpt-4-0125-preview":           OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4-1106-preview":           OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4-vision-preview":         OpenAITokenModel(usd_cents_per_million_input_tokens=10e2,   usd_cents_per_million_output_tokens=30e2),
    "gpt-4-32k":                    OpenAITokenModel(usd_cents_per_million_input_tokens=60e2,   usd_cents_per_million_output_tokens=120e2),
    "gpt-3.5-turbo":                OpenAITokenModel(usd_cents_per_million_input_tokens=50,     usd_cents_per_million_output_tokens=1.5e2),
    "gpt-3.5-turbo-0125":           OpenAITokenModel(usd_cents_per_million_input_tokens=50,     usd_cents_per_million_output_tokens=1.5e2),
    "gpt-3.5-turbo-1106":           OpenAITokenModel(usd_cents_per_million_input_tokens=1e2,    usd_cents_per_million_output_tokens=2e2),
    "gpt-3.5-turbo-0613":           OpenAITokenModel(usd_cents_per_million_input_tokens=1.5e2,  usd_cents_per_million_output_tokens=2e2),
    "gpt-3.5-turbo-0301":           OpenAITokenModel(usd_cents_per_million_input_tokens=1.5e2,  usd_cents_per_million_output_tokens=2e2),
    "gpt-3.5-turbo-16k":            OpenAITokenModel(usd_cents_per_million_input_tokens=3e2,    usd_cents_per_million_output_tokens=4e2),
    "gpt-3.5-turbo-16k-0613":       OpenAITokenModel(usd_cents_per_million_input_tokens=3e2,    usd_cents_per_million_output_tokens=4e2),
    "gpt-3.5-turbo-instruct":       OpenAITokenModel(usd_cents_per_million_input_tokens=1.5e2,  usd_cents_per_million_output_tokens=2e2),
    "gpt-3.5-turbo-instruct-0914":  OpenAITokenModel(usd_cents_per_million_input_tokens=1.5e2,  usd_cents_per_million_output_tokens=2e2),
    "davinci-002":                  OpenAITokenModel(usd_cents_per_million_input_tokens=2e2,    usd_cents_per_million_output_tokens=2e2),
    "babbage-002":                  OpenAITokenModel(usd_cents_per_million_input_tokens=40,     usd_cents_per_million_output_tokens=40),
}

FINE_TUNING_MODELS = {
    "gpt-3.5-turbo":    OpenAITokenModel(usd_cents_per_million_input_tokens=3e2,    usd_cents_per_million_output_tokens=6e2),
    "davinci-002":      OpenAITokenModel(usd_cents_per_million_input_tokens=12e2,   usd_cents_per_million_output_tokens=12e2),
    "babbage-002":      OpenAITokenModel(usd_cents_per_million_input_tokens=1.6e2,  usd_cents_per_million_output_tokens=1.6e2),
}

IMAGE_MODELS = {
    "dall-e-2": { # default
        "256x256":      OpenAIImageModelResolution(usd_cents_per_image=1.6),
        "512x512":      OpenAIImageModelResolution(usd_cents_per_image=1.8),
        "1024x1024":    OpenAIImageModelResolution(usd_cents_per_image=2), # default
    },
    "dall-e-3": {
        "standard": { # default
            "1024x1024": OpenAIImageModelResolution(usd_cents_per_image=4), # default
            "1792x1024": OpenAIImageModelResolution(usd_cents_per_image=8),
            "1024x1792": OpenAIImageModelResolution(usd_cents_per_image=8),
        },
        "hd": {
            "1024x1024": OpenAIImageModelResolution(usd_cents_per_image=8), # default
            "1792x1024": OpenAIImageModelResolution(usd_cents_per_image=12),
            "1024x1792": OpenAIImageModelResolution(usd_cents_per_image=12),
        }
    },
}

EMBEDDING_MODELS = {
    # Embedding Models
    "text-embedding-3-small": OpenAIEmbeddingModel(usd_cents_per_million_tokens=2),
    "text-embedding-3-large": OpenAIEmbeddingModel(usd_cents_per_million_tokens=13),
    "text-embedding-ada-002": OpenAIEmbeddingModel(usd_cents_per_million_tokens=10),
}

TTS_MODELS = {
    # Text-to-speech models
    "tts-1":            OpenAITextToSpeechModel(usd_cents_per_million_chars=15e2),
    "tts-1-1106":       OpenAITextToSpeechModel(usd_cents_per_million_chars=15e2),
    "tts-1-hd":         OpenAITextToSpeechModel(usd_cents_per_million_chars=30e2),
    "tts-1-hd-1106":    OpenAITextToSpeechModel(usd_cents_per_million_chars=30e2),
}

TRANSCRIPTION_MODELS = {
    # Transcription models
    "whisper-1": OpenAITranscriptionModel(usd_cents_per_input_minute=0.6),
}

MODERATION_MODELS = {
    "text-moderation-latest":   OpenAIModerationModel(),
    "text-moderation-stable":   OpenAIModerationModel(),
    "text-moderation-007":      OpenAIModerationModel(),
}

# fmt: on
