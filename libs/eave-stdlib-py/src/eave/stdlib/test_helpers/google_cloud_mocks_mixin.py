from typing import Any, override
import unittest.mock

from google.cloud.kms import CryptoKeyVersion, GetCryptoKeyVersionRequest, MacSignRequest, MacSignResponse, MacVerifyRequest, MacVerifyResponse
from google.cloud.secretmanager import AccessSecretVersionRequest, AccessSecretVersionResponse, SecretPayload
from eave.stdlib.checksum import generate_checksum
from eave.stdlib.test_helpers.mocking_mixin import MockingMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin


class GoogleCloudMocksMixin(MockingMixin, RandomDataMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_google_secret_manager_mocks()
        self._add_google_kms_mocks()

    def _add_google_secret_manager_mocks(self) -> None:
        def _access_secret_version(
            request: AccessSecretVersionRequest | dict[str, str] | None = None,
            *,
            name: str | None = None,
            **kwargs: Any,
        ) -> AccessSecretVersionResponse:
            if isinstance(request, AccessSecretVersionRequest):
                resolved_name = request.name
            elif isinstance(request, dict) and "name" in request:
                resolved_name = request["name"]
            elif name:
                resolved_name = name
            else:
                raise ValueError("bad name")

            data = self.anybytes(f"secret:{resolved_name}")
            data_crc32 = generate_checksum(data)

            return AccessSecretVersionResponse(
                name=resolved_name,
                payload=SecretPayload(
                    data=data,
                    data_crc32c=data_crc32,
                ),
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.secretmanager.SecretManagerServiceClient.access_secret_version",
                side_effect=_access_secret_version,
            )
        )

    def _add_google_kms_mocks(self) -> None:
        def _mac_sign(request: MacSignRequest) -> MacSignResponse:
            mac = self.anybytes()
            return MacSignResponse(
                verified_data_crc32c=True,
                name=request.name,
                mac=mac,
                mac_crc32c=generate_checksum(mac),
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.mac_sign",
                side_effect=_mac_sign,
            )
        )

        def _mac_verify(request: MacVerifyRequest) -> MacVerifyResponse:
            return MacVerifyResponse(
                verified_data_crc32c=True,
                verified_mac_crc32c=True,
                name=request.name,
                success=True,
                verified_success_integrity=True,
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.mac_verify",
                side_effect=_mac_verify,
            )
        )

        def _get_crypto_key_version(request: GetCryptoKeyVersionRequest) -> CryptoKeyVersion:
            return CryptoKeyVersion(
                name=request.name,
                algorithm=CryptoKeyVersion.CryptoKeyVersionAlgorithm.HMAC_SHA256,
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.get_crypto_key_version",
                side_effect=_get_crypto_key_version,
            )
        )
