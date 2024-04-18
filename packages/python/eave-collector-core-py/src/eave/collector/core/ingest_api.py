from dataclasses import dataclass

import aiohttp

from .config import EAVE_API_BASE_URL
from .datastructures import DataIngestRequestBody, EventType


@dataclass
class SpanBaseModel:
    events: list[str]
    event_type: EventType


# def to_json(span: ReadableSpan, indent: int = 4) -> str | None:
#     if not span._attributes:
#         return None

#     # TODO: add new attrs to the paylaod
#     statement = str(span._attributes.get(SpanAttributes.DB_STATEMENT))
#     params = typing.cast(list[str] | None, span._attributes.get(DB_PARAMS))
#     struct = DatabaseStructure.from_str(str(span._attributes.get(DB_STRUCTURE))) or DatabaseStructure.UNKNOWN

#     f_span = DatabaseEventPayload(
#         statement=statement,
#         parameters=params,
#         timestamp=time.time(),
#         db_structure=struct,
#     ).to_dict()

#     return json.dumps(f_span, indent=indent)

# asyncio.run(requests_util.make_request( # TODO: dont depend on our internal stdlib; this needs to be published to public
#     config=CoreApiEndpointConfiguration(
#         path="/ingest",
#         auth_required=False,
#         team_id_required=False,
#         signature_required=False,
#         origin_required=False,
#     ),
#     input=SpanBaseModel(
#         events=list(filter(None, [
#             to_json(span) for span in spans
#         ])),
#         event_type=EventType.dbevent
#     ),
#     origin=EaveApp.eave_api,
#     addl_headers={
#         EAVE_CLIENT_ID_HEADER: self.config.client_id,
#         EAVE_CLIENT_SECRET_HEADER: self.config.client_secret,
#     },
# ))


async def send_batch(event_type: EventType, events: list[str]) -> None:
    async with aiohttp.ClientSession() as session:
        body = DataIngestRequestBody(event_type=event_type, events=events)
        await session.request(
            method="POST",
            url=f"{EAVE_API_BASE_URL}/v1/ingest",
            data=body.to_json(),
            compress="gzip",
            headers={
                "eave-client-id": "TKTKTK",
                "eave-client-secret": "TKTKTK",
            },
        )
