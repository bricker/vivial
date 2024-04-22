import os

EAVE_API_BASE_URL = os.getenv("EAVE_API_BASE_PUBLIC", "https://api.eave.fyi")

# We don't call `os.getenv()` here so that the value can be read lazily.
EAVE_CREDENTIALS_ENV_KEY = "EAVE_CREDENTIALS"
