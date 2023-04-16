from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def get_subscription(
    input: eave_ops.GetSubscription.RequestBody, request: fastapi.Request
) -> eave_ops.GetSubscription.ResponseBody:
    logger.info("subscriptions.get_subscription")
    await eave_request_util.validate_signature_or_fail(request=request)

    async with eave_db.get_async_session() as db_session:
        team = await eave_request_util.get_team_or_fail(session=db_session, request=request)

        subscription_orm = await eave_orm.SubscriptionOrm.one_or_exception(
            team_id=team.id,
            source=input.subscription.source,
            session=db_session,
        )

        document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

    document_reference_public = (
        eave_models.DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
    )

    return eave_ops.GetSubscription.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription_orm),
        document_reference=document_reference_public,
    )


async def create_subscription(
    input: eave_ops.CreateSubscription.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.CreateSubscription.ResponseBody:
    logger.debug("subscriptions.create_subscription")
    await eave_request_util.validate_signature_or_fail(request=request)

    async with eave_db.get_async_session() as db_session:
        team = await eave_request_util.get_team_or_fail(session=db_session, request=request)

        subscription_orm = await eave_orm.SubscriptionOrm.one_or_none(
            team_id=team.id, source=input.subscription.source, session=db_session
        )

        if subscription_orm is None:
            subscription_orm = eave_orm.SubscriptionOrm(
                team_id=team.id,
                source=input.subscription.source,
                document_reference_id=input.document_reference.id if input.document_reference is not None else None,
            )

            db_session.add(subscription_orm)
            await db_session.commit()
            response.status_code = HTTPStatus.CREATED
        else:
            response.status_code = HTTPStatus.OK

        document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

    document_reference_public = (
        eave_models.DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
    )

    return eave_ops.CreateSubscription.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription_orm),
        document_reference=document_reference_public,
    )


async def delete_subscription(
    input: eave_ops.DeleteSubscription.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    logger.debug("subscriptions.delete_subscription")
    await eave_request_util.validate_signature_or_fail(request=request)

    async with eave_db.get_async_session() as db_session:
        team = await eave_request_util.get_team_or_fail(session=db_session, request=request)

        subscription_orm = await eave_orm.SubscriptionOrm.one_or_none(
            team_id=team.id, source=input.subscription.source, session=db_session
        )

        if subscription_orm is not None:
            await db_session.delete(subscription_orm)
            await db_session.commit()

    response.status_code = HTTPStatus.OK
    return response
