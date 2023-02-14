import json
from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException, Request, Response
from pydantic import UUID4, BaseModel, EmailStr

import eave.internal.slack as _slack
from eave.internal.database import session_factory
import eave.internal.util
from eave.internal.orm import AccessRequestOrm, PromptOrm, SubscriptionOrm, TeamOrm
from eave.public.models import DocumentReferencePublic, SubscriptionPublic, TeamPublic
from eave.public.shared import DocumentContentInput, PromptInput, SubscriptionInput


class GetStatus:
    class ResponseBody(BaseModel):
        status = "1"

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

class SavePrompt:
    class RequestBody(BaseModel):
        prompt: PromptInput

    @staticmethod
    async def handler(input: RequestBody, response: Response) -> None:
        async with session_factory() as session:
            prompt = PromptOrm(
                prompt=input.prompt.prompt,
                response=input.prompt.response
            )

            session.add(prompt)
            await session.commit()

        response.status_code = HTTPStatus.ACCEPTED
