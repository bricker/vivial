import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi

async def query(
    input: eave_ops.GetSlackSource.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackSource.ResponseBody:
    # TODO: db query
    # TODO: doing lookup by slack team id will reqruire adding an index on slack team id to db orm
    pass