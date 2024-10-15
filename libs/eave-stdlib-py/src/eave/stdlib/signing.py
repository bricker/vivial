import base64
import enum
import hashlib
from dataclasses import dataclass
import time
from typing import Literal, Optional, cast
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, utils
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eave_origins import EaveApp

from google.cloud import kms

from . import checksum
from . import exceptions as eave_exceptions
from . import util as eave_util
from .logging import LogContext

_CRYPTO_KEY_VERSION_CACHE: dict[str, kms.CryptoKeyVersion] = {}

def get_key_version(key_version_path: str) -> kms.CryptoKeyVersion:
    kms_client = kms.KeyManagementServiceClient()
    key_version = _CRYPTO_KEY_VERSION_CACHE.get(key_version_path)

    if not key_version:
        key_version_request = kms.GetCryptoKeyVersionRequest(name=key_version_path)
        key_version = kms_client.get_crypto_key_version(request=key_version_request)
        _CRYPTO_KEY_VERSION_CACHE[key_version_path] = key_version

    return key_version

def mac_sign_b64(*, data: str | bytes) -> str:
    """
    Signs the data with GCP KMS, and returns the base64-encoded signature
    """
    kms_client = kms.KeyManagementServiceClient()

    key_version_path = SHARED_CONFIG.jws_signing_key_version_path
    key_version = get_key_version(key_version_path)

    message_bytes = eave_util.ensure_bytes(data)
    data_crc32c = checksum.generate_checksum(message_bytes)

    sign_request = kms.MacSignRequest(name=key_version.name, data=message_bytes, data_crc32c=data_crc32c)
    sign_response = kms_client.mac_sign(request=sign_request)

    if sign_response.verified_data_crc32c is False:
        raise eave_exceptions.InvalidChecksumError("data crc32c failed verification on server")
    if sign_response.name != sign_request.name:
        raise eave_exceptions.InvalidChecksumError("unexpected key name")

    checksum.validate_checksum_or_exception(data=sign_response.mac, checksum=sign_response.mac_crc32c)
    return eave_util.b64encode(sign_response.mac)


def mac_verify_or_exception(*,
    kid: str,
    message: str | bytes, mac_b64: str | bytes,
) -> Literal[True]:
    """
    Verifies the signature matches the message.
    Either raises or returns True.
    The return value is to help you, the developer, understand that if this function doesn't throw,
    then the signature is verified.
    """
    kms_client = kms.KeyManagementServiceClient()

    # Verify the MAC sig with the same key version that was used to create it.
    key_version_path_dict = kms_client.parse_crypto_key_version_path(SHARED_CONFIG.jws_signing_key_version_path)
    key_version_path_dict["crypto_key_version"] = kid
    key_version_path = kms_client.crypto_key_version_path(**key_version_path_dict)

    message_bytes = eave_util.ensure_bytes(message)
    data_crc32c = checksum.generate_checksum(message_bytes)

    mac_bytes = base64.b64decode(mac_b64)
    mac_crc32c = checksum.generate_checksum(mac_bytes)

    verify_request = kms.MacVerifyRequest(name=key_version_path, data=message_bytes, data_crc32c=data_crc32c, mac_crc32c=mac_crc32c)
    verify_response = kms_client.mac_verify(request=verify_request)

    if verify_response.verified_data_crc32c is False:
        raise eave_exceptions.InvalidChecksumError("data crc32c failed verification on server")
    if verify_response.verified_mac_crc32c is False:
        raise eave_exceptions.InvalidChecksumError("mac crc32c failed verification on server")
    if verify_response.name != verify_request.name:
        raise eave_exceptions.InvalidChecksumError("unexpected key name")
    if verify_response.success is False:
        raise eave_exceptions.InvalidChecksumError("mac verification failed")
    if verify_response.verified_success_integrity != verify_response.success:
        raise eave_exceptions.InvalidChecksumError("mac verification integrity failed")

    return True
