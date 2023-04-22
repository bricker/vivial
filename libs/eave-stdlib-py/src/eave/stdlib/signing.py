from dataclasses import dataclass
import enum
import hashlib
from eave.stdlib.eave_origins import EaveOrigin
from google.cloud import kms
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, ec, rsa

from eave.stdlib.config import shared_config
from . import checksum

KMS_KEYRING_LOCATION = "global"
KMS_KEYRING_NAME = "primary"

class SigningAlgorithm(enum.Enum):
    RS256 = "RS256"
    ES256 = "ES256"

@dataclass
class SigningKeyDetails:
    id: str
    version: str
    algorithm: SigningAlgorithm

_SIGNING_KEYS = {
    EaveOrigin.eave_api.value: SigningKeyDetails(
        id="eave-api-signing-key",
        version="1",
        algorithm=SigningAlgorithm.ES256,
    ),
    EaveOrigin.eave_www.value: SigningKeyDetails(
        id="eave-www-signing-key",
        version="1",
        algorithm=SigningAlgorithm.ES256,
    ),
    EaveOrigin.eave_github_app.value: SigningKeyDetails(
        id="eave-github-app-signing-key-02",
        version="1",
        algorithm=SigningAlgorithm.ES256,
    ),
    EaveOrigin.eave_slack_app.value: SigningKeyDetails(
        id="eave-slack-app-signing-key",
        version="1",
        algorithm=SigningAlgorithm.ES256,
    ),
    EaveOrigin.eave_atlassian_app.value: SigningKeyDetails(
        id="eave-atlassian-app-signing-key",
        version="1",
        algorithm=SigningAlgorithm.ES256,
    ),
    "github_api_client": SigningKeyDetails(
        id="eave-github-app-signing-key-01",
        version="2",
        algorithm=SigningAlgorithm.RS256,
    ),
}

def get_key(signer: str) -> SigningKeyDetails:
    return _SIGNING_KEYS[signer]

class InvalidSignatureError(InvalidSignature):
    pass

def sign(signing_key: SigningKeyDetails, message: str) -> str:
    kms_client = kms.KeyManagementServiceClient()

    key_version_name = kms_client.crypto_key_version_path(
        project=shared_config.google_cloud_project,
        location=KMS_KEYRING_LOCATION,
        key_ring=KMS_KEYRING_NAME,
        crypto_key=signing_key.id,
        crypto_key_version=signing_key.version,
    )

    message_bytes = message.encode()
    digest = hashlib.sha256(message_bytes).digest()
    digest_crc32c = checksum.generate_checksum(data=digest)

    sign_response = kms_client.asymmetric_sign(
        request={
            "name": key_version_name,
            "digest": {"sha256": digest},
            "digest_crc32c": digest_crc32c
        }
    )

    if sign_response.verified_digest_crc32c is False:
        raise checksum.InvalidChecksumError()
    if sign_response.name != key_version_name:
        raise checksum.InvalidChecksumError()

    checksum.validate_checksum_or_exception(
        data=sign_response.signature,
        checksum=sign_response.signature_crc32c.value
    )

    return sign_response.signature.decode()

def validate_signature_or_exception(signing_key: SigningKeyDetails, message: str, signature: str) -> None:
    kms_client = kms.KeyManagementServiceClient()

    key_version_name = kms_client.crypto_key_version_path(
        project=shared_config.google_cloud_project,
        location=KMS_KEYRING_LOCATION,
        key_ring=KMS_KEYRING_NAME,
        crypto_key=signing_key.id,
        crypto_key_version=signing_key.version,
    )

    message_bytes = message.encode()
    digest = hashlib.sha256(message_bytes).digest()

    public_key_from_kms = kms_client.get_public_key(request={"name": key_version_name})
    public_key_from_pem = serialization.load_pem_public_key(
        data=public_key_from_kms.pem.encode(),
        backend=default_backend()
    )
    sha256 = hashes.SHA256()

    match signing_key.algorithm:
        case SigningAlgorithm.RS256:
            assert isinstance(public_key_from_pem, rsa.RSAPublicKey)
            pad = padding.PKCS1v15()
            public_key_from_pem.verify(
                signature=signature.encode(),
                data=digest,
                padding=pad,
                algorithm=utils.Prehashed(sha256),
            )
        case SigningAlgorithm.ES256:
            assert isinstance(public_key_from_pem, ec.EllipticCurvePublicKey)
            public_key_from_pem.verify(
                signature=signature.encode(),
                data=digest,
                signature_algorithm=ec.ECDSA(utils.Prehashed(sha256)),
            )
        case _:
            raise InvalidSignatureError(f"Unsupported algorithm: {signing_key.algorithm}")
