### get_services_from_repo

#### system

```

You will be provided a GitHub organization name, a repository name, and the directory hierarchy for that repository (starting from the root of the repository). Your task is to create a short, human-readable name and a description for any public HTTP services hosted in this repository. It's likely that there is exactly one service in the repository, however there may be more than one in the case of a monorepo hosting multiple applications, and there may be none in the case of a repository hosting only shared library code, developer tools, configuration, etc.

The directory hierarchy will be delimited by three exclamation points, and formatted this way:

- <directory name>
    - <directory name>
        - <file name>
        - <file name>
    - <directory name>
        - <file name>
    - ...

The service name(s) will be used in a high-level system architecture diagram. Go through the hierarchy a few times before you make your decision, each time refining your understanding of the repository.

Output your answer as a JSON array of objects, with each object containing the following keys:

- "service_name": the name that you created for the service
- "service_description": the description that you wrote for the service
- "service_root": The path to the directory in the provided hierarchy that can be considered the root directory of the service.

Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.

```

#### user

```

GitHub organization: eave-fyi

Repository: eave-monorepo

Directory Hierarchy:
!!!


- apps/slack
    - apps/slack/eave
        - apps/slack/eave/slack
            - apps/slack/eave/slack/requests
                - apps/slack/eave/slack/requests/warmup.py
                - apps/slack/eave/slack/requests/event_processor.py
                - apps/slack/eave/slack/requests/__init__.py
                - apps/slack/eave/slack/requests/event_callback.py
            - apps/slack/eave/slack/brain
                - apps/slack/eave/slack/brain/base.py
                - apps/slack/eave/slack/brain/intent_processing.py
                - apps/slack/eave/slack/brain/communication.py
                - apps/slack/eave/slack/brain/message_prompts.py
                - apps/slack/eave/slack/brain/subscription_management.py
                - apps/slack/eave/slack/brain/document_management.py
                - apps/slack/eave/slack/brain/context_building.py
                - apps/slack/eave/slack/brain/document_metadata.py
                - apps/slack/eave/slack/brain/core.py
            - apps/slack/eave/slack/slack_app.py
            - apps/slack/eave/slack/__init__.py
            - apps/slack/eave/slack/event_handlers.py
            - apps/slack/eave/slack/slack_models.py
            - apps/slack/eave/slack/app.py
            - apps/slack/eave/slack/config.py
    - apps/slack/bin
    - apps/slack/socketmode.py

!!!
```

### get_dependencies

#### system

```

        You will be given a GitHub organization name, a repository name, and some code from that repository. The code will be delimited by three exclamation marks. Your task is to find the APIs and services that the code depends on, which will then be used to create a high-level system architecture diagram.

        To perform this task, follow these steps:

        1. Find references to well-known, common third-party services in the code. For example, there may be references to Google Cloud, AWS, Redis, Postgres, Slack API, SendGrid.

        2. Find references to internal services. For example: Analytics, Core API, Authentication, Users API, GraphQL, Logging, Storage, Database.

        3. Once you've gone through the code and have a better understanding of its purpose and context, go through it a few more times and adjust your list if necessary based on what you've learned.

        4. For each service, either use one of the provided known service names if it makes sense to do so, otherwise create a short, human-readable name for the service.

        5. Write a 1-paragraph explanation of what the service does and how it fits into the system architecture.

        The code might not have any references to other systems. If you don't think there are any, don't force it.


Output your answer as a JSON array of objects, with each object containing the following keys:

- "service_name": the name that you created for the service
- "service_description": the description that you wrote for the service

Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.


```

#### user

```

GitHub organization: eave-fyi

Repository: eave-monorepo

Known service names: Slack API, Eave Core API, Eave Logging, Eave Cache, Google Cloud Tasks, Eave Analytics, Eave Stdlib, Starlette, Eave Slack App, App Config, Slack App, Slack Bolt, Eave Slack, OpenAI API

 Code:
!!!


from eave.stdlib.core_api.models.subscriptions import SubscriptionInfo
from . import message_prompts


from eave.stdlib.logging import eaveLogger
from .intent_processing import IntentProcessingMixin


class Brain(IntentProcessingMixin):
    async def process_message(self) -> None:
        eaveLogger.debug("Brain.process_message", self.eave_ctx)

        await self.load_data()

        subscription_response = await self.get_subscription()
        if subscription_response.subscription:
            self.subscriptions.append(
                SubscriptionInfo(
                    subscription=subscription_response.subscription,
                    document_reference=subscription_response.document_reference,
                )
            )

        i_am_mentioned = await self.message.check_eave_is_mentioned()
        if i_am_mentioned is True:
            """
            Eave is mentioned in this message.
            1. Acknowledge receipt of the message.
            1. If she's being asked for thread information, handle that and stop processing.
            1. Otherwise, send a preliminary response and continue processing.
            """
            await self.acknowledge_receipt()

            self.message_action = await message_prompts.message_action(context=self.message_context)

            self.log_event(
                event_name="eave_mentioned",
                event_description="Eave was mentioned in Slack",
                opaque_params={
                    "action": self.message_action,
                },
            )

        else:
            """
            Eave is not mentioned in this message.
            1. Lookup an existing subscription for this source.
            1. If she is not subscribed, then ignore the message and stop processing.
            1. Otherwise, continue processing.
            """
            if len(self.subscriptions) == 0:
                eaveLogger.debug("Eave is not subscribed to this thread; ignoring.", self.eave_ctx)
                return

            self.message_action = message_prompts.MessageAction.REFINE_DOCUMENTATION

        self.log_event(
            event_name="slack_eave_action",
            event_description="Eave is taking an action based on a Slack message",
            opaque_params={
                "action": self.message_action,
            },
        )

        await self.handle_action(message_action=self.message_action)

    async def process_shortcut_event(self) -> None:
        await self.acknowledge_receipt()

        # source = eave_models.SubscriptionSource(
        #     event=eave_models.SubscriptionSourceEvent.slack_message,
        #     id=message.subscription_id,
        # )

        # response = await eave_models.client.get_or_create_subscription(source=source)
        # manager = DocumentManager(message=message, subscription=response.subscription)
        # await manager.process_message()

    async def load_data(self) -> None:
        user_profile = await self.message.get_user_profile()
        self.user_profile = user_profile

        expanded_text = await self.message.get_expanded_text()
        if expanded_text is None:
            eaveLogger.warning(
                "slack message expanded_text is unexpectedly None",
                self.eave_ctx,
                {"message_text": self.message.text},
            )

            # FIXME: Brain should allow None expanded_text so it can retry.
            expanded_text = ""

        self.expanded_text = expanded_text

        await self.build_message_context()


!!!
```

