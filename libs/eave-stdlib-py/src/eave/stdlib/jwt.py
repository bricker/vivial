import enum
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Self

from . import exceptions, signing
from . import util as eave_util

ALLOWED_CLOCK_DRIFT_SECONDS = 60

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
    kid: int

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
    signing_key: SigningKeyDetails,
    purpose: str,
    issuer: str,
    audience: str,
    subject: str,
    issued_at: int | None = None,
    not_before: int | None = None,
    jwt_id: str | None = None,
    exp_minutes: int = 10,
) -> str:
    # all time formats are expected to be in the format of an integer
    # number of seconds since epoch (aka NumericDate)
    # https://www.rfc-editor.org/rfc/rfc7519
    now = int(time.time())
    exp = now + (60 * exp_minutes)

    if issued_at is None:
        issued_at = now
    if not_before is None:
        not_before = issued_at
    if jwt_id is None:
        jwt_id = str(uuid.uuid4())

    jws_header = JWSHeader(typ="JWT", alg=signing_key.algorithm.value, kid=signing_key.version)
    jwt_payload = JWTRegisteredClaims(
        iss=issuer,
        aud=audience,
        sub=subject,
        iat=issued_at,
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

    signature_b64 = signing.sign_b64(signing_key=signing_key, data=jws.message)
    jws.signature = signature_b64
    return str(jws)

def validate_jws_or_exception(
    *,
    encoded_jws: str,
    expected_issuer: str,
    expected_audience: str,
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

    jws = JWS.from_str(jwt_encoded=encoded_jws)

    signing.verify_signature_or_exception(
        message=jws.message,
        signature=jws.signature,
    )

    now = time.time()
    grace_now = now + ALLOWED_CLOCK_DRIFT_SECONDS
    expires_at = float(jws.payload.exp)
    issued_at = float(jws.payload.iat)
    not_before = float(jws.payload.nbf)

    if not (
        jws.payload.aud == expected_audience
        and jws.payload.nbf
        and issued_at < (now + ALLOWED_CLOCK_DRIFT_SECONDS) # allow clock drift
        and round(expired_at) == round(
            expected_expiry.timestamp()
        )  # conversion between datetime and float is inexact wrt decimal precision. For our needs, second precision is adequate.
        and now > not_before
    ):
        raise exceptions.InvalidJWSError()
    else:
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

    jwt_a = JWT.from_str(jwt_encoded=jwt_encoded_a)
    jwt_b = JWT.from_str(jwt_encoded=jwt_encoded_b)

    if (jwt_encoded_a == jwt_encoded_b) or (jwt_a.signature == jwt_b.signature):
        raise exceptions.InvalidJWSError("matching tokens or signatures")

    signing.verify_signature_or_exception(
        signing_key=signing_key,
        message=jwt_a.message,
        signature=jwt_a.signature,
    )

    signing.verify_signature_or_exception(
        signing_key=signing_key,
        message=jwt_b.message,
        signature=jwt_b.signature,
    )

    if not (
        jwt_a.payload.iss == jwt_b.payload.iss
        and jwt_a.payload.aud == jwt_b.payload.aud
        and jwt_a.payload.sub == jwt_b.payload.sub
        and jwt_a.payload.jti == jwt_b.payload.jti
        and jwt_a.payload.iat == jwt_b.payload.iat
        and jwt_a.payload.nbf == jwt_b.payload.nbf
    ):
        raise exceptions.InvalidJWSError()
    else:
        return True