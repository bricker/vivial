from eave.stdlib.core_api.models import BaseResponseModel


# NOTE: keep in sync w/ mirror definition collector-core!
# (until pydantic dep is removed or we decide to have collectors depend on it too)
class DataCollectorConfig(BaseResponseModel):
    user_table_name_patterns: list[str]
    primary_key_patterns: list[str]
    foreign_key_patterns: list[str]
