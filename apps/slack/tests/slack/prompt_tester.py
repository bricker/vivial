# import logging
# import os
# import sys

# from dotenv import load_dotenv

# load_dotenv()

# import asyncio
# import json

# import eave.slack.brain
# import eave.slack.message_prompts
# import eave.slack.slack_models
# import eave.stdlib.logging
# import eave.stdlib.openai_client

# eave.stdlib.logging.setup_logging(level=logging.DEBUG)
# from eave.stdlib import logger

# jsonstring = """
# {
#   "channel": "C051LAJE4ES",
#   "channel_type": "channel",
#   "client_msg_id": "1dc45313-c09c-4f10-96d5-3486fad0db5e",
#   "event_ts": "1680720718.400389",
#   "parent_user_id": "U03H23466MN",
#   "team": "T03G5LV6R7Y",
#   "text": "<@U04JKG95GUC> is there any existing documentation about this?",
#   "thread_ts": "1680637189.965309",
#   "ts": "1680720718.400389",
#   "type": "message",
#   "user": "U03H23466MN"
# }
# """


# async def test_slack_message_processing() -> None:
#     logger.info("test_slack_message_processing")
#     event = json.loads(jsonstring)
#     message = eave.slack.slack_models.SlackMessage(event)
#     brain = eave.slack.brain.Brain(message=message)
#     await brain.process_message()


# async def test_action_prompt() -> None:
#     logger.info("test_action_prompt")
#     event = json.loads(jsonstring)
#     message = eave.slack.slack_models.SlackMessage(event)
#     brain = eave.slack.brain.Brain(message=message)
#     await brain.load_data()
#     message_action = await eave.slack.message_prompts.message_action(context=brain.message_context)
#     logger.info(message_action)


# async def test_document_builder() -> None:
#     logger.info("test_document_builder")
#     event = json.loads(jsonstring)
#     message = eave.slack.slack_models.SlackMessage(event)
#     brain = eave.slack.brain.Brain(message=message)
#     await brain.load_data()
#     doc = await brain.build_documentation()

#     with open("/tmp/doc.html", "w+") as f:
#         f.write("<p>CATEGORIES:</p>")
#         f.write("<ol>")
#         c = doc
#         while c.parent is not None:
#             f.write(f"<li>{c.parent.title}</li>")
#             c = c.parent
#         f.write("</ol>")

#         f.write("<hr>")
#         f.write(f"<p>TITLE: {doc.title}</p>")
#         f.write("<hr>")

#         f.write(doc.content)

#     os.system("open /tmp/doc.html")


# if __name__ == "__main__":
#     asyncio.run(test_action_prompt())
