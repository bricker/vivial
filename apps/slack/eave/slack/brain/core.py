from . import message_prompts


from eave.stdlib.logging import eaveLogger
from .intent_processing import IntentProcessingMixin


class Brain(IntentProcessingMixin):
    async def process_message(self) -> None:
        eaveLogger.debug("Brain.process_message", extra=self.eave_ctx)

        await self.load_data()

        subscription_response = await self.get_subscription()
        if subscription_response.subscription:
            self.subscriptions.append(subscription_response.subscription)

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
                event_description="Eave was mentioned somewhere",
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
                eaveLogger.debug("Eave is not subscribed to this thread; ignoring.", extra=self.eave_ctx)
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
                extra=self.eave_ctx.set(
                    {
                        "message_text": self.message.text,
                    }
                ),
            )

            # FIXME: Brain should allow None expanded_text so it can retry.
            expanded_text = ""

        self.expanded_text = expanded_text

        await self.build_message_context()
