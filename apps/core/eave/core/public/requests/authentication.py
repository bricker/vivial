# from datetime import datetime

# import eave.core.internal.database as eave_db
# import eave.core.public.requests.util as request_util
# import eave.stdlib.core_api.operations as eave_ops
# import eave.stdlib.exceptions as eave_exceptions
# import fastapi
# import sqlalchemy.exc
# from eave.core.internal.orm.auth_token import AuthTokenOrm
# from eave.stdlib import logger


# async def refresh_access_token(
#     input: eave_ops.RefreshAccessToken.RequestBody, request: fastapi.Request
# ) -> eave_ops.RefreshAccessToken.ResponseBody:
#     eave_state = request_util.get_eave_state(request=request)

#     async with eave_db.async_session.begin() as db_session:
#         try:
#             old_auth_token = await AuthTokenOrm.find_and_verify_or_exception(
#                 session=db_session,
#                 log_context=eave_state.log_context,
#                 access_token=input.access_token,
#                 refresh_token=input.refresh_token,
#                 aud=eave_state.eave_origin.value,
#                 allow_expired=True,
#             )
#         except sqlalchemy.exc.SQLAlchemyError as e:
#             # If the passed-in tokens aren't found, then return an UNAUTHORIZED error instead of NOT FOUND for improved security.
#             logger.error(
#                 "auth token request invalid. The tokens are invalid or the account has been deactivated.",
#                 exc_info=e,
#                 extra=eave_state.log_context,
#             )
#             raise eave_exceptions.InvalidAuthError() from e

#         new_auth_token = await AuthTokenOrm.create_token_pair_for_account(
#             session=db_session,
#             log_context=eave_state.log_context,
#             account=old_auth_token.account,
#             audience=eave_state.eave_origin,
#         )

#         # TODO: Is there a reason to keep old auth tokens around if they're invalid?
#         old_auth_token.auth_token.invalidated = datetime.utcnow()
#         await db_session.delete(old_auth_token.auth_token)

#     return eave_ops.RefreshAccessToken.ResponseBody(
#         access_token=str(new_auth_token.access_token),
#         refresh_token=str(new_auth_token.refresh_token),
#     )
