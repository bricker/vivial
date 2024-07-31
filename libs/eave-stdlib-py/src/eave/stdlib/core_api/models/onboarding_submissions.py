from eave.stdlib.core_api.models import BaseResponseModel


class OnboardingSubmission(BaseResponseModel):
    languages: list[str]
    platforms: list[str]
    frameworks: list[str]
    databases: list[str]
    third_party_libs: list[str]
