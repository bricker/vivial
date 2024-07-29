from eave.stdlib.core_api.models import BaseResponseModel


class OnboardingSubmission(BaseResponseModel):
    response_data: dict[str, list[str]]
