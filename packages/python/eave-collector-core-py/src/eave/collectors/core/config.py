import os


def eave_api_base_url() -> str:
    return os.getenv("EAVE_API_BASE_PUBLIC", "https://api.eave.fyi")


def eave_credentials_headers() -> dict[str, str]:
    credentials_str = os.getenv("EAVE_CREDENTIALS")
    if not credentials_str:
        return {}

    credentials = credentials_str.split(":")

    if len(credentials) != 2:
        raise ValueError('invalid credentials format. Expected format: "client_id:client_secret"')

    return {
        "eave-client-id": credentials[0],
        "eave-client-secret": credentials[1],
    }


def eave_env() -> str:
    return os.getenv("EAVE_ENV", default="production")


def is_development() -> bool:
    return eave_env() == "development"


def batch_maxsize() -> int:
    if is_development():
        return 0
    else:
        return 0  # TODO: make this >0


def batch_maxage_seconds() -> int:
    if is_development():
        return 0
    else:
        return 30
