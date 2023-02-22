import json
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import UUID4, BaseModel, EmailStr

import eave.internal.google_oauth
import eave.internal.slack as _slack
import eave.internal.util
from eave.internal.database import session_factory
from eave.internal.orm import (
    AccessRequestOrm,
    AccountOrm,
    AuthProvider,
    SubscriptionOrm,
    TeamOrm,
)
from eave.internal.settings import APP_SETTINGS
from eave.public.models import DocumentReferencePublic, SubscriptionPublic, TeamPublic
from eave.public.shared import DocumentContentInput, DocumentPlatform, SubscriptionInput


class GetStatus:
    class ResponseBody(BaseModel):
        status = "1"
        service = "api"

    @staticmethod
    def handler() -> ResponseBody:
        return GetStatus.ResponseBody()


class CreateAccessRequest:
    class RequestBody(BaseModel):
        visitor_id: Optional[UUID4]
        email: EmailStr
        opaque_input: Optional[eave.internal.util.JsonObject]

    @staticmethod
    async def handler(input: RequestBody, response: Response) -> Response:
        async with session_factory() as session:
            access_request = await AccessRequestOrm.find_one(session=session, email=input.email)

            if access_request is None:
                access_request = AccessRequestOrm(
                    visitor_id=input.visitor_id,
                    email=input.email,
                    opaque_input=json.dumps(input.opaque_input),
                )

                session.add(access_request)
                await session.commit()

                response.status_code = HTTPStatus.CREATED

                # Notify #sign-ups Slack channel.
                _slack.notify_slack(email=input.email, visitor_id=input.visitor_id, opaque_input=input.opaque_input)
            else:
                response.status_code = HTTPStatus.OK

        return response


class UpsertDocument:
    class RequestBody(BaseModel):
        document: DocumentContentInput
        subscription: SubscriptionInput

    class ResponseBody(BaseModel):
        team: TeamPublic
        subscription: SubscriptionPublic
        document_reference: DocumentReferencePublic

    @staticmethod
    async def handler(input: RequestBody, request: Request, response: Response) -> ResponseBody:
        state = eave.internal.util.StateWrapper(request.state)
        if state.team_id is None:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        async with session_factory() as session:
            team = await TeamOrm.find_one(team_id=state.team_id, session=session)
            if team is None:
                raise HTTPException(HTTPStatus.FORBIDDEN)

            subscription = await SubscriptionOrm.find_one(
                team_id=team.id, source=input.subscription.source, session=session
            )
            if subscription is None:
                raise HTTPException(HTTPStatus.NOT_FOUND)

            destination = await team.get_document_destination(session=session)
            existing_document_reference = await subscription.get_document_reference(session=session)
            if existing_document_reference is None:
                document_reference = await destination.create_document(
                    document=input.document,
                    session=session,
                )

                await session.commit()
                subscription.document_reference_id = document_reference.id
                await session.commit()

            else:
                document_reference = await destination.update_document(
                    document=input.document,
                    document_reference=existing_document_reference,
                )

        # Eventually this endpoint will accept the input and push to the destination offline.
        response.status_code = HTTPStatus.ACCEPTED

        return UpsertDocument.ResponseBody(
            team=TeamPublic.from_orm(team),
            subscription=SubscriptionPublic.from_orm(subscription),
            document_reference=DocumentReferencePublic.from_orm(document_reference),
        )


class GetSubscription:
    class RequestBody(BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(BaseModel):
        team: TeamPublic
        subscription: SubscriptionPublic
        document_reference: Optional[DocumentReferencePublic]

    @staticmethod
    async def handler(input: RequestBody, request: Request, response: Response) -> ResponseBody:
        state = eave.internal.util.StateWrapper(request.state)
        if state.team_id is None:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        async with session_factory() as session:
            team = await TeamOrm.find_one(team_id=state.team_id, session=session)
            if team is None:
                raise HTTPException(HTTPStatus.FORBIDDEN)

            subscription_orm = await SubscriptionOrm.find_one(
                team_id=team.id,
                source=input.subscription.source,
                session=session,
            )
            if subscription_orm is None:
                raise HTTPException(HTTPStatus.NOT_FOUND)

            document_reference_orm = await subscription_orm.get_document_reference(session=session)

        document_reference_public = (
            DocumentReferencePublic.from_orm(document_reference_orm) if document_reference_orm is not None else None
        )

        return GetSubscription.ResponseBody(
            team=TeamPublic.from_orm(team),
            subscription=SubscriptionPublic.from_orm(subscription_orm),
            document_reference=document_reference_public,
        )


class CreateSubscription:
    class RequestBody(BaseModel):
        subscription: SubscriptionInput

    class ResponseBody(BaseModel):
        team: TeamPublic
        subscription: SubscriptionPublic
        document_reference: Optional[DocumentReferencePublic]

    @staticmethod
    async def handler(input: RequestBody, request: Request, response: Response) -> ResponseBody:
        state = eave.internal.util.StateWrapper(request.state)
        if state.team_id is None:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        async with session_factory() as session:
            team = await TeamOrm.find_one(team_id=state.team_id, session=session)
            if team is None:
                raise HTTPException(HTTPStatus.FORBIDDEN)

            subscription_orm = await SubscriptionOrm.find_one(
                team_id=team.id, source=input.subscription.source, session=session
            )

            if subscription_orm is None:
                subscription_orm = SubscriptionOrm(
                    team_id=team.id,
                    source=input.subscription.source,
                )

                session.add(subscription_orm)
                await session.commit()
                response.status_code = HTTPStatus.CREATED
            else:
                response.status_code = HTTPStatus.OK

            document_reference_orm = await subscription_orm.get_document_reference(session=session)

        document_reference_public = (
            DocumentReferencePublic.from_orm(document_reference_orm) if document_reference_orm is not None else None
        )

        return CreateSubscription.ResponseBody(
            team=TeamPublic.from_orm(team),
            subscription=SubscriptionPublic.from_orm(subscription_orm),
            document_reference=document_reference_public,
        )


class GoogleOauthInit:
    @staticmethod
    async def handler() -> Response:
        oauth_flow_info = eave.internal.google_oauth.get_oauth_flow_info()
        response = RedirectResponse(url=oauth_flow_info.authorization_url)
        response.set_cookie(
            **shared_state_cookie_params(),
            value=oauth_flow_info.state,
        )
        return response


class GoogleOauthCallback:
    class RequestBody(BaseModel):
        state: Optional[str]
        code: Optional[str]
        error: Optional[str]

    @staticmethod
    async def handler(input: RequestBody, request: Request, response: Response) -> None:
        state = request.cookies.get("ev_oauth_state")
        assert state is not None

        credentials = eave.internal.google_oauth.get_oauth_credentials(uri=str(request.url), state=state)

        assert credentials.id_token is not None
        token = eave.internal.google_oauth.decode_id_token(id_token=credentials.id_token)
        userid = token.get("sub")
        assert userid is not None
        given_name = token.get("given_name")

        async with session_factory() as session:
            account_orm = await AccountOrm.find_one(session=session, auth_provider=AuthProvider.google, auth_id=userid)

            if account_orm is None:
                team = TeamOrm(
                    name=f"{given_name}'s Team" if given_name is not None else "Your Team",
                    document_platform=DocumentPlatform.unspecified,
                )

                session.add(team)
                await session.commit()

                account_orm = AccountOrm(
                    team_id=team.id,
                    auth_provider=AuthProvider.google,
                    auth_id=userid,
                    oauth_token=credentials.id_token,
                )

                session.add(account_orm)

            account_orm.oauth_token = credentials.id_token
            await session.commit()

        response = RedirectResponse(url=f"{APP_SETTINGS.eave_www_base}/setup")
        response.delete_cookie(**shared_state_cookie_params())


def shared_state_cookie_params() -> eave.internal.util.JsonObject:
    params = {
        "key": "ev_oauth_state",
        "domain": APP_SETTINGS.eave_cookie_domain,
        "secure": True,
        "httponly": True,
    }

    return params
