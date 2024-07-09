import os
import google.cloud.secretmanager
from crc32c import crc32c

def get_secret(name: str) -> str:
    # Allow overrides from the environment
    if (envval := os.environ.get(name)) and envval != "(not set)":
        return envval

    secrets_client = google.cloud.secretmanager.SecretManagerServiceClient()
    fqname = secrets_client.secret_version_path(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        secret=name,
        secret_version="latest",  # noqa: S106
    )
    response = secrets_client.access_secret_version(request={"name": fqname})
    data = response.payload.data

    data_crc32c = response.payload.data_crc32c
    if crc32c(data) != data_crc32c:
        raise ValueError("invalid checksum")

    return data.decode("UTF-8")
