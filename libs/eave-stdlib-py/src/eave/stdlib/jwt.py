import base64
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import enum
import json
import time
from typing import Optional, Self
import uuid
from . import signing
from . import exceptions

@dataclass
class JWTRegisteredClaims:
    iss: str
    aud: str
    sub: str
    iat: str
    exp: str
    nbf: str
    jti: str

    @classmethod
    def from_b64(cls, payload_encoded: str) -> Self:
        jsonstr = base64.b64decode(payload_encoded).decode()
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
        return base64.b64encode(json.dumps(self.__dict__).encode()).decode()

class JWTPurpose(enum.Enum):
    access = "access"
    refresh = "refresh"

@dataclass
class JWTHeader:
    typ: str
    alg: str
    pur: str

    @classmethod
    def from_b64(cls, header_encoded: str) -> Self:
        jsonstr = base64.b64decode(header_encoded).decode()
        jsonv = json.loads(jsonstr)
        return cls(typ=jsonv["typ"], alg=jsonv["alg"], pur=jsonv["pur"])

    def to_b64(self) -> str:
        return base64.b64encode(json.dumps(self.__dict__).encode()).decode()

@dataclass
class JWT:
    header: JWTHeader
    payload: JWTRegisteredClaims
    signature: str

    @classmethod
    def from_str(cls, jwt_encoded: str) -> Self:
        header_encoded, payload_encoded, signature_provided = jwt_encoded.split(".")
        header = JWTHeader.from_b64(header_encoded=header_encoded)
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
        return f"{self.message}.{self.signature}"

def create_jwt(
        signing_key: signing.SigningKeyDetails,
        purpose: JWTPurpose,
        iss: str,
        aud: str,
        sub: str,
        iat: Optional[str] = None,
        nbf: Optional[str] = None,
        jti: Optional[str] = None,
        exp_minutes: int = 10
) -> JWT:
    now = time.time()
    exp = str(now + (60 * exp_minutes))

    if iat is None:
        iat = str(now - 60) # allow for 60s of clock drift
    if nbf is None:
        nbf = iat
    if jti is None:
        jti = str(uuid.uuid4())

    jwt_header = JWTHeader(typ="JWT", alg=signing_key.algorithm.value, pur=purpose.value)
    jwt_payload = JWTRegisteredClaims(
        iss=iss,
        aud=aud,
        sub=sub,
        iat=iat,
        exp=exp,
        nbf=iat,
        jti=jti,
    )

    message = f"{jwt_header.to_b64()}.{jwt_payload.to_b64()}"
    signature = signing.sign(signing_key=signing_key, message=message)
    signature_b64 = base64.b64encode(signature.encode()).decode()

    return JWT(
        header=jwt_header,
        payload=jwt_payload,
        signature=signature_b64
    )

def validate_jwt_or_exception(
        jwt_encoded: str,
        expected_issuer: str,
        expected_audience: str,
        expected_subject: str,
        expected_expiry: datetime,
        expected_jti: str,
        signing_key: signing.SigningKeyDetails,
        expired_ok: bool = False,
    ) -> None:
    jwt = JWT.from_str(jwt_encoded=jwt_encoded)
    signing.validate_signature_or_exception(
        signing_key=signing_key,
        message=jwt.message,
        signature=jwt.signature,
    )

    now = time.time()
    exp = float(jwt.payload.exp)
    iat = float(jwt.payload.iat)
    nbf = float(jwt.payload.nbf)

    # TODO: Validate this
    if not (
        jwt.payload.iss == expected_issuer
        and jwt.payload.aud == expected_audience
        and jwt.payload.sub == expected_subject
        and jwt.payload.jti == expected_jti
        and iat < now
        and (expired_ok or exp > now)
        and (expired_ok or exp < (now + (60*10)))
        and exp == expected_expiry.timestamp()
        and now > nbf
    ):
        raise exceptions.InvalidJWTError()

def validate_jwt_pair_or_exception(
        jwt_encoded_a: str,
        jwt_encoded_b: str,
        signing_key: signing.SigningKeyDetails,
    ) -> None:

    assert jwt_encoded_a != jwt_encoded_b

    jwt_a = JWT.from_str(jwt_encoded=jwt_encoded_a)
    jwt_b = JWT.from_str(jwt_encoded=jwt_encoded_b)

    assert jwt_a.signature != jwt_b.signature

    signing.validate_signature_or_exception(
        signing_key=signing_key,
        message=jwt_a.message,
        signature=jwt_a.signature,
    )

    signing.validate_signature_or_exception(
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
        raise exceptions.InvalidJWTError()
