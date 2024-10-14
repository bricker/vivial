import enum
import json
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Self

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LogContext

from . import exceptions, signing
from . import util as eave_util

threading.local["log_context"] = LogContext()

ALLOWED_CLOCK_DRIFT_SECONDS = 60

class InvalidJWTError(Exception):
    pass

@dataclass
class JWTRegisteredClaims:
    """
    https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
    """
    iss: str
    aud: str
    sub: str
    iat: int
    exp: int
    nbf: int
    jti: str
    pur: str
    """JWT purpose, eg 'access' or 'refresh'"""

    @classmethod
    def from_b64(cls, payload_encoded: str) -> Self:
        jsonstr = eave_util.b64decode(payload_encoded)
        jsonv = json.loads(jsonstr)
        return cls(
            iss=jsonv["iss"],
            aud=jsonv["aud"],
            sub=jsonv["sub"],
            iat=jsonv["iat"],
            exp=jsonv["exp"],
            nbf=jsonv["nbf"],
            jti=jsonv["jti"],
            pur=jsonv["pur"],
        )

    def to_b64(self) -> str:
        return eave_util.b64encode(json.dumps(self.__dict__))

@dataclass
class JWSHeader:
    typ: str
    alg: str
    kid: str

    @classmethod
    def from_b64(cls, header_encoded: str) -> Self:
        jsonstr = eave_util.b64decode(header_encoded)
        jsonv = json.loads(jsonstr)
        return cls(typ=jsonv["typ"], alg=jsonv["alg"], kid=jsonv["kid"])

    def to_b64(self) -> str:
        return eave_util.b64encode(json.dumps(self.__dict__))


@dataclass
class JWS:
    header: JWSHeader
    payload: JWTRegisteredClaims
    signature: str

    @classmethod
    def from_str(cls, jwt_encoded: str) -> Self:
        header_encoded, payload_encoded, signature_provided = jwt_encoded.split(".")
        header = JWSHeader.from_b64(header_encoded=header_encoded)
        payload = JWTRegisteredClaims.from_b64(payload_encoded=payload_encoded)

        return cls(
            header=header,
            payload=payload,
            signature=signature_provided,
        )

    @property
    def message(self) -> str:
        return f"{self.header.to_b64()}.{self.payload.to_b64()}"

    def to_str(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.message}.{self.signature}"


def create_jws(
    *,
    purpose: str,
    issuer: str,
    audience: str,
    subject: str,
    not_before: int | None = None,
    jwt_id: str | None = None,
    max_age_minutes: int = 10,
    ctx: LogContext,
) -> str:
    # all time formats are expected to be in the format of an integer
    # number of seconds since epoch (aka NumericDate)
    # https://www.rfc-editor.org/rfc/rfc7519
    now = int(time.time())
    exp = now + (60 * max_age_minutes)

    if not_before is None:
        not_before = now
    if jwt_id is None:
        jwt_id = str(uuid.uuid4())

    crypto_key_version = SHARED_CONFIG.jws_signing_key_version_path

    jws_header = JWSHeader(typ="JWT", alg=signing_key.algorithm.value, kid=signing_key.version)
    jwt_payload = JWTRegisteredClaims(
        iss=issuer,
        aud=audience,
        sub=subject,
        iat=now,
        exp=exp,
        nbf=not_before,
        jti=jwt_id,
        pur=purpose,
    )

    jws = JWS(
        header=jws_header,
        payload=jwt_payload,
        signature="",
    )

    signature_b64 = signing.mac_sign_b64(data=jws.message, ctx=ctx)
    jws.signature = signature_b64
    return str(jws)

def validate_jws_or_exception(
    *,
    encoded_jws: str,
    expected_issuer: str,
    expected_audience: str,
    ctx: LogContext,
) -> JWS:
    """
    Validate the JWT according to https://datatracker.ietf.org/doc/html/rfc7519#section-7.2
    Validate the JWS according to https://datatracker.ietf.org/doc/html/rfc7515#section-5.2
    Validates the claims in the given JWT against what we expect.
    Also verifies the signature.
    Either raises or returns True.
    The return value is to help you, the developer, understand that if this function doesn't throw,
    then the JWT is valid and verified.
    """

    # This should be before signature verification because that makes a network request that takes some time.
    now = int(time.time())

    jws = JWS.from_str(jwt_encoded=encoded_jws)

    signing.mac_verify_or_exception(
        kid=jws.header.kid,
        message=jws.message,
        mac_b64=jws.signature,
        ctx=ctx,
    )

    expires_at = float(jws.payload.exp)
    not_before = float(jws.payload.nbf)

    if jws.payload.iss != expected_issuer:
        raise InvalidJWTError("iss")
    if jws.payload.aud != expected_audience:
        raise InvalidJWTError("aud")
    if now < not_before - ALLOWED_CLOCK_DRIFT_SECONDS:
        raise InvalidJWTError("nbf")
    if now > expires_at + ALLOWED_CLOCK_DRIFT_SECONDS:
        raise InvalidJWTError("exp")

    return jws


def validate_jws_pair_or_exception(
    jwt_encoded_a: str,
    jwt_encoded_b: str,
    signing_key: signing.SigningKeyDetails,
) -> Literal[True]:
    """
    Verifies the the two JWTs (most commonly an Access Token and Refresh Token pair) belong together.
    Notably, this function DOES NOT validate any claims. For that, use `validate_jwt_or_exception`.
    Either raises or returns True.
    The return value is to help you, the developer, understand that if this function doesn't throw,
    then the JWTs belong together and are both verified.
    """

    jws_a = JWS.from_str(jwt_encoded=jwt_encoded_a)
    jws_b = JWS.from_str(jwt_encoded=jwt_encoded_b)

    if (jwt_encoded_a == jwt_encoded_b) or (jws_a.signature == jws_b.signature):
        raise exceptions.InvalidJWSError("matching tokens or signatures")

    if not jws_a.payload.iss == jws_b.payload.iss:
        raise exceptions.InvalidJWSError("iss")
    if not jws_a.payload.aud == jws_b.payload.aud:
        raise exceptions.InvalidJWSError("aud")
    if not jws_a.payload.sub == jws_b.payload.sub:
        raise exceptions.InvalidJWSError("sub")
    if not jws_a.payload.jti == jws_b.payload.jti:
        raise exceptions.InvalidJWSError("jti")

    return True
