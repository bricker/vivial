import hmac
from typing import Optional

from eave.stdlib.config import shared_config

ALGORITHM = "sha256"

SIGNATURE_HEADER_NAME = "eave-signature"
TEAM_ID_HEADER_NAME = "eave-team-id"

class InvalidSignatureError(Exception):
    pass

def sign(payload: str, team_id: Optional[str] = None) -> str:
    secret_key = shared_config.eave_signing_secret

    hm = hmac.new(key=secret_key.encode(), digestmod=ALGORITHM)

    if team_id is not None:
        hm.update(msg=team_id.encode())

    hm.update(msg=payload.encode())
    signature = hm.hexdigest()
    return signature

def compare_signatures(expected: str, actual: str) -> bool:
    return hmac.compare_digest(expected, actual)
