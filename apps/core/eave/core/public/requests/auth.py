import hashlib
from http import HTTPStatus
from datetime import datetime
from typing import Tuple
import uuid
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.signing as eave_signing
import eave.stdlib.util as eave_util
import apps.core.eave.core.public.requests.state as eave_state
import apps.core.eave.core.public.requests.util as request_util
from eave.core import EAVE_API_SIGNING_KEY, EAVE_API_JWT_ISSUER
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def request_access_token(input: eave_ops.RequestAccessToken.RequestBody, request: fastapi.Request) -> eave_ops.RequestAccessToken.ResponseBody:
    state = eave_state.EaveRequestState(request.state)

    async with eave_db.get_async_session() as db_session:
        account = await eave_orm.AccountOrm.one_or_exception(
            session=db_session,
            exchange_offer=input.exchange_offer
        )

        new_access_token_jwt, new_refresh_token_jwt, new_auth_token_orm = make_token_pair(
            account_id=account.id,
            eave_origin=state.eave_origin,
        )

        db_session.add(new_auth_token_orm)
        await db_session.commit()

    return eave_ops.RequestAccessToken.ResponseBody(
        access_token=new_access_token_jwt.to_str(),
        refresh_token=new_refresh_token_jwt.to_str(),
    )

async def refresh_access_token(input: eave_ops.RefreshAccessToken.RequestBody, request: fastapi.Request) -> eave_ops.RefreshAccessToken.ResponseBody:
    state = eave_state.EaveRequestState(request.state)

    eave_jwt.validate_jwt_pair_or_exception(
        jwt_encoded_a=input.access_token,
        jwt_encoded_b=input.refresh_token,
        signing_key=EAVE_API_SIGNING_KEY
    )

    async with eave_db.get_async_session() as db_session:
        old_auth_token_orm = await eave_orm.AuthTokenOrm.one_or_exception(
            session=db_session,
            access_token_hashed=eave_util.sha256digest(input.access_token),
            refresh_token_hashed=eave_util.sha256digest(input.refresh_token),
        )

        if old_auth_token_orm.invalidated is not None:
            logger.error("auth token invalidated", extra=request_util.log_context(request))
            raise fastapi.HTTPException(HTTPStatus.UNAUTHORIZED)

        account = await eave_orm.AccountOrm.one_or_exception(
            session=db_session,
            id=old_auth_token_orm.account_id,
        )

        new_access_token_jwt, new_refresh_token_jwt, new_auth_token_orm = make_token_pair(
            account_id=account.id,
            eave_origin=state.eave_origin,
        )

        db_session.add(new_auth_token_orm)

        # Is there a reason to keep old auth tokens around if they're invalid?
        old_auth_token_orm.invalidated = datetime.utcnow()
        await db_session.delete(old_auth_token_orm)
        await db_session.commit()

    return eave_ops.RefreshAccessToken.ResponseBody(
        access_token=new_access_token_jwt.to_str(),
        refresh_token=new_refresh_token_jwt.to_str(),
    )

def make_token_pair(account_id: uuid.UUID, eave_origin: eave_origins.EaveOrigin) -> Tuple[eave_jwt.JWT, eave_jwt.JWT, eave_orm.AuthTokenOrm]:
    sub = str(account_id)
    aud = eave_origin.value

    new_access_token_jwt = eave_jwt.create_jwt(
        signing_key=EAVE_API_SIGNING_KEY,
        purpose=eave_jwt.JWTPurpose.access,
        iss=EAVE_API_JWT_ISSUER,
        aud=aud,
        sub=sub,
    )

    new_refresh_token_jwt = eave_jwt.create_jwt(
        signing_key=EAVE_API_SIGNING_KEY,
        purpose=eave_jwt.JWTPurpose.refresh,
        iss=EAVE_API_JWT_ISSUER,
        aud=aud,
        sub=sub,
        jti=new_access_token_jwt.payload.jti,
        exp_minutes=(60*24*30) # 30 days. If the user goes 30 days without logging in, they will have to login again.
    )

    new_auth_token_orm = eave_orm.AuthTokenOrm(
        account_id=account_id,
        iss=EAVE_API_JWT_ISSUER,
        aud=aud,
        jti=new_access_token_jwt.payload.jti,
        access_token=eave_util.sha256digest(new_access_token_jwt.to_str()),
        refresh_token=eave_util.sha256digest(new_refresh_token_jwt.to_str()),
        expires=datetime.fromtimestamp(float(new_access_token_jwt.payload.exp)),
    )

    return (new_access_token_jwt, new_refresh_token_jwt, new_auth_token_orm)