import typing
import json
import time
from opentelemetry.sdk.trace import ReadableSpan

from eave.tracing.core.datastructures import DatabaseEventPayload, DatabaseOperation


class EaveReadableSpan(ReadableSpan):
    def to_json(self, indent: int = 4) -> typing.Any:
        # parent_id = None
        # if self.parent is not None:
        #     parent_id = f"0x{trace_api.format_span_id(self.parent.span_id)}"

        # start_time = None
        # if self._start_time:
        #     start_time = util.ns_to_iso_str(self._start_time)

        # end_time = None
        # if self._end_time:
        #     end_time = util.ns_to_iso_str(self._end_time)

        status = {
            "status_code": str(self._status.status_code.name),
        }
        if self._status.description:
            status["description"] = self._status.description


        assert self._attributes
        f_span = DatabaseEventPayload(
            table_name=str(self._attributes.get("db.name")),
            operation=DatabaseOperation(str(self._attributes.get("db.operation")).upper()),
            parameters=None,
            timestamp=time.time(),
        ).to_dict()

        """
            -> db.statement: Str(INSERT INTO virtual_events (team_id, readable_name, description, view_id, updated) VALUES ($1::UUID, $2::VARCHAR, $3::VARCHAR, $4::VARCHAR, $5::TIMESTAMP WITHOUT TIME ZONE) RETURNING virtual_events.id, virtual_events.created)
            -> db.system: Str(postgresql)
            -> db.params: Str((UUID('5ea57c57-ed6a-4d60-b2a0-e7a605fc47be'), 'Dummy event 99.29', 'boo fuzz fazz bizz bazz fazz fizz fazz bar', '99.29', None))
            -> net.peer.name: Str(localhost)
            -> net.peer.port: Int(5432)
            -> db.name: Str(eave-test)
            -> db.user: Str(eave_db_user)
        """

        # f_span = {
        #     "name": self._name,
        #     "context": self._format_context(self._context)
        #     if self._context
        #     else None,
        #     "kind": str(self.kind),
        #     # "parent_id": parent_id,
        #     # "start_time": start_time,
        #     # "end_time": end_time,
        #     "status": status,
        #     "attributes": self._format_attributes(self._attributes),
        #     "events": self._format_events(self._events),
        #     "links": self._format_links(self._links),
        #     "resource": json.loads(self.resource.to_json()),
        # }

        return json.dumps(f_span, indent=indent)