import base64
from dataclasses import dataclass
import hashlib
import hmac
import enum
import json
import time
from typing import Self
import uuid
from . import signing

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

@dataclass
class JWTHeader:
    typ: str
    alg: str

    @classmethod
    def from_b64(cls, header_encoded: str) -> Self:
        jsonstr = base64.b64decode(header_encoded).decode()
        jsonv = json.loads(jsonstr)
        return cls(typ=jsonv["typ"], alg=jsonv["alg"])

    def to_b64(self) -> str:
        return base64.b64encode(json.dumps(self.__dict__).encode()).decode()

@dataclass
class JWT:
    header: JWTHeader
    payload: JWTRegisteredClaims
    signature: str

    @classmethod
    def from_str(cls, jwt_encoded: str) -> Self:
        [header_encoded, payload_encoded, signature_provided] = jwt_encoded.split(".")
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

    def hash(self) -> str:
        hash = hashlib.sha256(self.to_str().encode())
        return hash.hexdigest()

def create_jwt(issuer: str, audience: str, subject: str, signing_key: signing.SigningKeyDetails) -> JWT:
    now = time.time()
    iat = now - 60 # allow for 60s of clock drift
    exp = now + (60 * 10) # 10 minutes
    jti = uuid.uuid4() # This is not currently used.

    jwt_header = JWTHeader(typ="JWT", alg=signing_key.algorithm.value)
    jwt_payload = JWTRegisteredClaims(
        iss=issuer,
        aud=audience,
        sub=subject,
        iat=f"{iat}",
        exp=f"{exp}",
        nbf=f"{iat}",
        jti=str(jti),
    )

    message = f"{jwt_header.to_b64()}.{jwt_payload.to_b64()}"
    signature = signing.sign(signing_key=signing_key, message=message)
    signature_b64 = base64.b64encode(signature.encode()).decode()

    return JWT(
        header=jwt_header,
        payload=jwt_payload,
        signature=signature_b64
    )

def validate_jwt_or_exception(jwt_encoded: str, signing_key: signing.SigningKeyDetails) -> None:
    jwt = JWT.from_str(jwt_encoded=jwt_encoded)
    signing.validate_signature_or_exception(
        signing_key=signing_key,
        message=jwt.message,
        signature=jwt.signature,
    )

    now = time.time()

    # TODO: Validate these
    # assert jwt.payload.iss
    # assert jwt.payload.aud
    # assert jwt.payload.sub
    # assert jwt.payload.jti
    assert float(jwt.payload.iat) < now
    assert float(jwt.payload.exp) > now
    assert float(jwt.payload.exp) < (now + (60*10))
    assert now > float(jwt.payload.nbf)
