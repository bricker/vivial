from eave.stdlib.core_api.operations import (
    CoreApiEndpoint,
    CoreApiEndpointConfiguration,
)


class MetabaseEmbeddingSSOOperation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/oauth/metabase",
        method="GET",
        auth_required=True,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
    )
