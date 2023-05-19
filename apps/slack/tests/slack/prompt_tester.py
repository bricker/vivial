import os
import sys
import textwrap
import uuid
from typing import Any
import eave.stdlib.core_api.enums
import asyncio
import json

import eave.slack.brain
import eave.slack.message_prompts
import eave.slack.slack_models
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.openai_client
from slack_bolt.async_app import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

import eave.stdlib.logging

logger = eave.stdlib.logging.eaveLogger

eave_team = eave_models.Team(
    id=uuid.uuid4(), name="Test Team", document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence
)

# TODO: This client isn't usable, needs a token
slack_context = AsyncBoltContext({"client": AsyncWebClient()})


async def test_slack_message_processing(fixture: dict[str, Any]) -> None:
    logger.info("test_slack_message_processing")
    message = eave.slack.slack_models.SlackMessage(fixture, slack_context=slack_context)
    brain = eave.slack.brain.Brain(message=message, slack_context=slack_context, eave_team=eave_team)
    await brain.process_message()


async def test_action_prompt(fixture: dict[str, Any]) -> None:
    logger.info("test_action_prompt")
    message = eave.slack.slack_models.SlackMessage(fixture, slack_context=slack_context)
    brain = eave.slack.brain.Brain(message=message, slack_context=slack_context, eave_team=eave_team)
    await brain.load_data()
    message_action = await eave.slack.message_prompts.message_action(context=brain.message_context)
    logger.info(message_action)


async def test_document_builder(fixture: dict[str, Any]) -> None:
    logger.info("test_document_builder")
    message = eave.slack.slack_models.SlackMessage(fixture, slack_context=slack_context)
    brain = eave.slack.brain.Brain(message=message, slack_context=slack_context, eave_team=eave_team)
    await brain.load_data()
    doc = await brain.build_documentation()

    filename = f"/tmp/eavedocs/{uuid.uuid4()}.html"
    with open(filename, "w+") as fd:
        c = doc
        crumbs: list[str] = []
        while c.parent is not None:
            crumbs.append(c.parent.title)
            c = c.parent

        fd.write(
            textwrap.dedent(
                """
            <html><head><style>
            body { font-family: system-ui; padding: 50px; width: 75%; }
            pre { background-color: black; color: white; padding: 20px; overflow: auto; }
            code { color:deeppink; }
            hr { color: lightgray; }
            th { background-color: lightgray; padding: 5px; }
            td { border: lightgray 1px solid; padding: 5px; }
            h1, h2, h3, h4, h5, h6 { border-bottom: 1px solid lightgray; }
            </style></head><body>
            """
            )
        )

        fd.write("<p>")
        fd.write(" > ".join(crumbs))
        fd.write("</p>")
        fd.write(f"<h1>{doc.title}</h1>")
        fd.write(doc.content)

        fd.write("</body></html>")

    os.system(f"open {filename}")


if __name__ == "__main__":
    testcase_name = sys.argv[1]
    fixture_name = sys.argv[2]
    testcase_func = getattr(sys.modules[__name__], testcase_name)

    with open(fixture_name) as f:
        fixture_string = f.read()

    fixture = json.loads(fixture_string)
    asyncio.run(testcase_func(fixture))
