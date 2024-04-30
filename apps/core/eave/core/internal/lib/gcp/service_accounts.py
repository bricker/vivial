from dataclasses import dataclass
from typing import Any
from eave.stdlib.config import SHARED_CONFIG
from google.oauth2 import service_account
import googleapiclient.discovery
import base64

class GoogleCloudServiceAccount:
    _attributes: dict[str, Any]
    email: str | None

    def __init__(self, attributes: dict[str, Any]) -> None:
        self._attributes = attributes
        self.email = attributes.get("email")

class GoogleCloudServiceAccountKey:
    _attributes: dict[str, Any]
    private_key: str | None

    def __init__(self, attributes: dict[str, Any]) -> None:
        self._attributes = attributes

        if private_key_data := attributes.get("privateKeyData"):
            # The privateKeyData field contains the base64-encoded service account key in JSON format.
            self.private_key = base64.b64decode(private_key_data).decode("utf-8")
        else:
            self.private_key = None

def create_service_account(account_id: str, display_name: str) -> GoogleCloudServiceAccount:
    service = googleapiclient.discovery.build("iam", "v1")

    service_account_attributes: dict[str, Any] = (
        service.projects()
        .serviceAccounts()
        .create(
            name=f"projects/{SHARED_CONFIG.google_cloud_project}",
            body={"accountId": account_id, "serviceAccount": {"displayName": display_name}},
        )
        .execute()
    )

    return GoogleCloudServiceAccount(attributes=service_account_attributes)

def create_service_account_key(service_account_email: str) -> GoogleCloudServiceAccountKey:
    service = googleapiclient.discovery.build("iam", "v1")

    service_account_key_attributes = (
        service.projects()
        .serviceAccounts()
        .keys()
        .create(name=f"projects/{SHARED_CONFIG.google_cloud_project}/serviceAccounts/{service_account_email}", body={})
        .execute()
    )

    return GoogleCloudServiceAccountKey(attributes=service_account_key_attributes)

def bind_service_account_key_to_bq_dataset(service_account_email: str) -> None:
    pass