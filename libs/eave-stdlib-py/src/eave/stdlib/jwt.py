import enum
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Self

from . import exceptions, signing
from . import util as eave_util


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
        )

    def to_b64(self) -> str:
        return eave_util.b64encode(json.dumps(self.__dict__))


class JWTPurpose(enum.Enum):
    access = "access"
    refresh = "refresh"


@dataclass
class JWSHeader:
    typ: str
    alg: str
    pur: str
    kid: str

    @classmethod
    def from_b64(cls, header_encoded: str) -> Self:
        jsonstr = eave_util.b64decode(header_encoded)
        jsonv = json.loads(jsonstr)
        return cls(typ=jsonv["typ"], alg=jsonv["alg"], pur=jsonv["pur"], kid=jsonv["kid"])

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


def create_encrypted_jws(
    signing_key: signing.SigningKeyDetails,
    purpose: JWTPurpose,
    iss: str,
    aud: str,
    sub: str,
    iat: int | None = None,
    nbf: int | None = None,
    jti: str | None = None,
    exp_minutes: int = 10,
) -> str:
    # all time formats are expected to be in the format of an integer
    # number of seconds since epoch (aka NumericDate)
    # https://www.rfc-editor.org/rfc/rfc7519
    now = int(time.time())
    exp = now + (60 * exp_minutes)

    if iat is None:
        iat = now - 60  # allow for 60s of clock drift
    if nbf is None:
        nbf = iat
    if jti is None:
        jti = str(uuid.uuid4())

    jws_header = JWSHeader(typ="JWT", alg=signing_key.algorithm.value, pur=purpose.value)
    jwt_payload = JWTRegisteredClaims(
        iss=iss,
        aud=aud,
        sub=sub,
        iat=iat,
        exp=exp,
        nbf=iat,
        jti=jti,
    )

    jws = JWS(
        header=jws_header,
        payload=jwt_payload,
        signature="",
    )

    signature_b64 = signing.sign_b64(signing_key=signing_key, data=jws.message)
    jws.signature = signature_b64

    encrypted_jws = signing.encrypt_b64(str(jws))
    return encrypted_jws

def validate_jws_or_exception(
    *,
    encrypted_jws: str,
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

    decrypted_jws = signing.decrypt(encrypted_jws)
    jws = JWS.from_str(jwt_encoded=decrypted_jws)

    signing.verify_signature_or_exception(
        message=jws.message,
        signature=jws.signature,
    )

    now = time.time()
    exp = float(jws.payload.exp)
    iat = float(jws.payload.iat)
    nbf = float(jws.payload.nbf)

    if not (
        jws.payload.iss == expected_issuer
        and jws.payload.aud == expected_audience
        and jws.payload.sub == expected_subject
        and jws.payload.jti == expected_jti
        and iat < now
        and (allow_expired or exp > now)
        and (allow_expired or exp < (now + (60 * 10)))
        and round(exp)
        == round(
            expected_expiry.timestamp()
        )  # conversion between datetime and float is inexact wrt decimal precision. For our needs, second precision is adequate.
        and now > nbf
    ):
        raise exceptions.InvalidJWSError()
    else:
        return jws


def validate_jwt_pair_or_exception(
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