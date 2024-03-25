import json
from datetime import datetime

import eave.pubsub_schemas

message = eave.pubsub_schemas.EaveEvent(
    event_name="run_tests",
    event_description="A developer ran the tests",
    event_source="tests",
    event_time=datetime.utcnow().isoformat(),
    eave_account_id="dev",
    eave_visitor_id="dev",
    eave_team_id="dev",
    opaque_params=json.dumps(
        {
            "foo": "bar",
        }
    ),
)

print(message)

serialized = message.SerializeToString()
print(serialized)
