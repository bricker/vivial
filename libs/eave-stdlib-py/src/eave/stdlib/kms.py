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

KMS_KEYRING_LOCATION = "global"
KMS_KEYRING_NAME = "primary"

_kms_client = kms.KeyManagementServiceClient()

def get_key(key_name: str) -> str:
    key_name = _kms_client.crypto_key_path(
        project=SHARED_CONFIG.google_cloud_project,
        location=KMS_KEYRING_LOCATION,
        key_ring=KMS_KEYRING_NAME,
        crypto_key=signing_key.id,
    )



def sign_b64(signing_key: SigningKeyDetails, data: str | bytes, ctx: LogContext) -> str:
    """
    Signs the data with GCP KMS, and returns the base64-encoded signature
    """
    kms_client = kms.KeyManagementServiceClient()

    key_version_name = kms_client.crypto_key_version_path(
        project=SHARED_CONFIG.google_cloud_project,
        location=KMS_KEYRING_LOCATION,
        key_ring=KMS_KEYRING_NAME,
        crypto_key=signing_key.id,
        crypto_key_version=signing_key.version,
    )

    message_bytes = eave_util.ensure_bytes(data)
    digest = hashlib.sha256(message_bytes).digest()
    digest_crc32c = checksum.generate_checksum(data=digest)

    sign_response = kms_client.asymmetric_sign(
        request={"name": key_version_name, "digest": {"sha256": digest}, "digest_crc32c": digest_crc32c}
    )

    if sign_response.verified_digest_crc32c is False:
        raise eave_exceptions.InvalidChecksumError()
    if sign_response.name != key_version_name:
        raise eave_exceptions.InvalidChecksumError()

    checksum.validate_checksum_or_exception(data=sign_response.signature, checksum=sign_response.signature_crc32c)

    return eave_util.b64encode(sign_response.signature)


def verify_signature_or_exception(
    signing_key: SigningKeyDetails, message: str | bytes, signature: str | bytes, ctx: LogContext
) -> Literal[True]:
    """
    Verifies the signature matches the message.
    Either raises or returns True.
    The return value is to help you, the developer, understand that if this function doesn't throw,
    then the signature is verified.
    """
    message_bytes = eave_util.ensure_bytes(message)
    signature_bytes = base64.b64decode(signature)

    public_key_from_pem = get_public_key(signing_key)

    digest = hashlib.sha256(message_bytes).digest()

    sha256 = hashes.SHA256()

    match signing_key.algorithm:
        case SigningAlgorithm.RS256:
            public_key_from_pem = cast(rsa.RSAPublicKey, public_key_from_pem)
            pad = padding.PKCS1v15()
            public_key_from_pem.verify(
                signature=signature_bytes,
                data=digest,
                padding=pad,
                algorithm=utils.Prehashed(sha256),
            )
            return True
        case SigningAlgorithm.ES256:
            public_key_from_pem = cast(ec.EllipticCurvePublicKey, public_key_from_pem)
            public_key_from_pem.verify(
                signature=signature_bytes,
                data=digest,
                signature_algorithm=ec.ECDSA(utils.Prehashed(sha256)),
            )
            return True
        case _:
            raise eave_exceptions.InvalidSignatureError(f"Unsupported algorithm: {signing_key.algorithm}")


def _fetch_public_key(signing_key: SigningKeyDetails) -> PublicKeyTypes:
    """
    Makes a network request to Google KMS to fetch the
    public key associated with `sigining_key`.
    """
    kms_client = kms.KeyManagementServiceClient()

    key_version_name = kms_client.crypto_key_version_path(
        project=SHARED_CONFIG.google_cloud_project,
        location=KMS_KEYRING_LOCATION,
        key_ring=KMS_KEYRING_NAME,
        crypto_key=signing_key.id,
        crypto_key_version=signing_key.version,
    )
    public_key_from_kms = kms_client.get_public_key(request={"name": key_version_name})
    public_key_from_pem = serialization.load_pem_public_key(
        data=public_key_from_kms.pem.encode(), backend=default_backend()
    )

    return public_key_from_pem


def get_public_key(signing_key: SigningKeyDetails) -> PublicKeyTypes:
    """
    Get the public key PEM associated with `signing_key`,
    or from an in-memory cache if previously computed.
    """
    if signing_key in _PUBLIC_KEYS_CACHE:
        return _PUBLIC_KEYS_CACHE[signing_key]
    result = _fetch_public_key(signing_key)
    _PUBLIC_KEYS_CACHE[signing_key] = result
    return result


def preload_public_keys() -> None:
    """
    Preloads all PEM public keys for all registered signing keys
    to accelerate signature verification middleware.
    """
    for signing_key in _SIGNING_KEYS.values():
        _PUBLIC_KEYS_CACHE[signing_key] = _fetch_public_key(signing_key)


def build_message_to_sign(
    method: str,
    path: str,
    ts: int,
    request_id: uuid.UUID | str,
    audience: EaveApp | str,
    origin: EaveApp | str,
    payload: str,
    team_id: Optional[uuid.UUID | str],
    account_id: Optional[uuid.UUID | str],
    ctx: Optional[LogContext] = None,
) -> str:
    signature_elements: list[str] = [
        str(origin),
        method,
        str(audience),
        path,
        str(ts),
        str(request_id),
        payload,
    ]

    if team_id:
        signature_elements.append(str(team_id))

    if account_id:
        signature_elements.append(str(account_id))

    signature_message = ":".join(signature_elements)
    return signature_message


def make_sig_ts() -> int:
    return int(time.time())