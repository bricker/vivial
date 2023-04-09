import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

import json
import asyncio
import eave.slack.brain
import eave.slack.slack_models

import eave.stdlib.logging
eave.stdlib.logging.setup_logging(level=logging.DEBUG)
from eave.stdlib import logger

jsonstring = """
{
  "blocks": [
    {
      "block_id": "DOIx",
      "elements": [
        {
          "elements": [
            {
              "type": "user",
              "user_id": "U04JKG95GUC"
            },
            {
              "text": " please document this thread",
              "type": "text"
            }
          ],
          "type": "rich_text_section"
        }
      ],
      "type": "rich_text"
    }
  ],
  "channel": "C051LAJE4ES",
  "channel_type": "channel",
  "client_msg_id": "1dc45313-c09c-4f10-96d5-3486fad0db5e",
  "event_ts": "1680720718.400389",
  "parent_user_id": "U03H23466MN",
  "team": "T03G5LV6R7Y",
  "text": "<@U04JKG95GUC> please document this thread",
  "thread_ts": "1680637189.965309",
  "ts": "1680720718.400389",
  "type": "message",
  "user": "U03H23466MN"
}
"""

async def test_request_processor() -> None:
    logger.info("test_request_processor")
    event = json.loads(jsonstring)
    message = eave.slack.slack_models.SlackMessage(event)
    brain = eave.slack.brain.Brain(message=message)
    await brain.process_message()

async def test_document_builder() -> None:
    logger.info("test_document_builder")
    event = json.loads(jsonstring)
    message = eave.slack.slack_models.SlackMessage(event)
    brain = eave.slack.brain.Brain(message=message)
    await brain.load_data()
    doc = await brain.build_documentation()

    with open("/tmp/doc.html", "w+") as f:
      f.write("<p>CATEGORIES:</p>")
      f.write("<ol>")
      c = doc
      while c.parent is not None:
        f.write(f"<li>{c.parent.title}</li>")
        c = c.parent
      f.write("</ol>")

      f.write("<hr>")
      f.write(f"<p>TITLE: {doc.title}</p>")
      f.write("<hr>")

      f.write(doc.content)

    os.system('open /tmp/doc.html')


if __name__ == "__main__":
    asyncio.run(test_document_builder())