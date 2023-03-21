import hmac
from typing import Optional

import fastapi
from eave_stdlib.config import shared_config

ALGORITHM = "sha256"

SIGNATURE_HEADER_NAME = "eave-signature"
TEAM_ID_HEADER_NAME = "eave-team-id"

class InvalidSignatureError(Exception):
    pass

async def sign(payload: str, team_id: Optional[str] = None) -> str:
    secret_key = await shared_config.eave_signing_secret

    hm = hmac.new(key=secret_key.encode(), digestmod=ALGORITHM)

    if team_id is not None:
        hm.update(msg=team_id.encode())

    hm.update(msg=payload.encode())
    signature = hm.hexdigest()
    return signature

async def validate_signature_or_fail(request: fastapi.Request) -> None:
    payload = await request.json()
    signature = request.headers.get(SIGNATURE_HEADER_NAME)
    team_id = request.headers.get(TEAM_ID_HEADER_NAME)

    if not signature or not payload:
        # reject None or empty strings
        raise InvalidSignatureError()

    expected_signature = await sign(payload=payload, team_id=team_id)
    if hmac.compare_digest(signature, expected_signature) == False:
        raise InvalidSignatureError()
