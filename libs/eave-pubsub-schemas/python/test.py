import json
import time

import eave.pubsub_schemas.generated.eave_user_action_pb2 as eave_user_action

message = eave_user_action.EaveUserAction(
    action=eave_user_action.EaveUserAction.Action(
        platform="test",
        name="run_tests",
        description="A developer ran the tests",
        eave_user_id="dev",
        opaque_params=json.dumps(
            {
                "foo": "bar",
            }
        ),
        user_ts=int(time.time()),
    ),
    message_source="eave-pubsub-schemas",
)

print(message)

serialized = message.SerializeToString()
print(serialized)
