import base64
from typing import Literal

from google.cloud import kms

from . import checksum
from . import util as eave_util

_CRYPTO_KEY_VERSION_CACHE: dict[str, kms.CryptoKeyVersion] = {}


class InvalidSignatureError(Exception):
    pass


def replace_key_version(*, kms_key_version_path: str, kms_key_version_name: str) -> str:
    # Verify the MAC sig with the same key version that was used to create it.
    key_version_path_dict = kms.KeyManagementServiceClient.parse_crypto_key_version_path(kms_key_version_path)
    key_version_path_dict["crypto_key_version"] = kms_key_version_name
    new_key_version_path = kms.KeyManagementServiceClient.crypto_key_version_path(**key_version_path_dict)
    return new_key_version_path


def get_key_version(kms_key_version_path: str) -> kms.CryptoKeyVersion:
    kms_client = kms.KeyManagementServiceClient()
    key_version = _CRYPTO_KEY_VERSION_CACHE.get(kms_key_version_path)

    if not key_version:
        key_version_request = kms.GetCryptoKeyVersionRequest(name=kms_key_version_path)
        key_version = kms_client.get_crypto_key_version(request=key_version_request)
        _CRYPTO_KEY_VERSION_CACHE[kms_key_version_path] = key_version

    return key_version


def mac_sign_b64(*, data: str | bytes, kms_key_version_path: str) -> str:
    """
    Signs the data with GCP KMS, and returns the base64-encoded signature
    """
    kms_client = kms.KeyManagementServiceClient()

    message_bytes = eave_util.ensure_bytes(data)
    data_crc32c = checksum.generate_checksum(message_bytes)

    sign_request = kms.MacSignRequest(name=kms_key_version_path, data=message_bytes, data_crc32c=data_crc32c)
    sign_response = kms_client.mac_sign(request=sign_request)

    if sign_response.verified_data_crc32c is False:
        raise checksum.InvalidChecksumError("data crc32c failed verification on server")
    if sign_response.name != sign_request.name:
        raise checksum.InvalidChecksumError("unexpected key name")

    checksum.validate_checksum_or_exception(data=sign_response.mac, checksum=sign_response.mac_crc32c)
    return eave_util.b64encode(sign_response.mac)


def mac_verify(
    *,
    message: str | bytes,
    mac_b64: str | bytes,
    kms_key_version_path: str,
) -> Literal[True]:
    """
    Verifies the signature matches the message.
    Either raises or returns True.
    The return value is to help you, the developer, understand that if this function doesn't throw,
    then the signature is verified.
    """
    kms_client = kms.KeyManagementServiceClient()
    message_bytes = eave_util.ensure_bytes(message)
    data_crc32c = checksum.generate_checksum(message_bytes)

    mac_bytes = base64.b64decode(mac_b64)
    mac_crc32c = checksum.generate_checksum(mac_bytes)

    verify_request = kms.MacVerifyRequest(
        name=kms_key_version_path,
        data=message_bytes,
        mac=mac_bytes,
        data_crc32c=data_crc32c,
        mac_crc32c=mac_crc32c,
    )
    verify_response = kms_client.mac_verify(
        request=verify_request,
    )

    if verify_response.verified_data_crc32c is False:
        raise checksum.InvalidChecksumError("data crc32c failed verification on server")
    if verify_response.verified_mac_crc32c is False:
        raise checksum.InvalidChecksumError("mac crc32c failed verification on server")
    if verify_response.name != verify_request.name:
        raise checksum.InvalidChecksumError("unexpected key name")
    if verify_response.success is False:
        raise InvalidSignatureError("mac verification failed")
    if verify_response.verified_success_integrity != verify_response.success:
        raise checksum.InvalidChecksumError("mac verification integrity failed")

    return True
