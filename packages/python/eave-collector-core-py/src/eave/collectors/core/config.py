import os


def eave_api_base_url() -> str:
    return os.getenv("EAVE_API_BASE_URL_PUBLIC", "https://api.eave.fyi")


def get_eave_credentials() -> str | None:
    return os.getenv("EAVE_CREDENTIALS")


def eave_credentials_headers() -> dict[str, str]:
    credentials_str = get_eave_credentials()
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


def queue_maxsize() -> int:
    if is_development():
        return 1
    else:
        return 1  # TODO: make this >0


def queue_flush_frequency_seconds() -> int:
    if is_development():
        return 0
    else:
        return 30
