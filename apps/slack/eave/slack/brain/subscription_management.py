import json
from eave.slack.brain.base import SubscriptionInfo
import eave.stdlib.core_api.models.subscriptions
import eave.stdlib.core_api.operations.subscriptions as eave_subscriptions
from .communication import CommunicationMixin
from ..config import SLACK_APP_CONFIG


class SubscriptionManagementMixin(CommunicationMixin):
    async def get_subscription(self) -> eave_subscriptions.GetSubscriptionRequest.ResponseBody:
        subscription = await eave_subscriptions.GetSubscriptionRequest.perform(
            ctx=self.eave_ctx,
            origin=SLACK_APP_CONFIG.eave_origin,
            team_id=self.eave_team.id,
            input=eave_subscriptions.GetSubscriptionRequest.RequestBody(
                subscription=eave.stdlib.core_api.models.subscriptions.SubscriptionInput(
                    source=self.message.subscription_source
                ),
            ),
        )
        return subscription

    async def create_subscription(self) -> eave_subscriptions.CreateSubscriptionRequest.ResponseBody:
        """
        Gets and returns the subscription if it already exists, otherwise creates and returns a new subscription.
        """
        subscription = await eave_subscriptions.CreateSubscriptionRequest.perform(
            ctx=self.eave_ctx,
            origin=SLACK_APP_CONFIG.eave_origin,
            team_id=self.eave_team.id,
            input=eave_subscriptions.CreateSubscriptionRequest.RequestBody(
                subscription=eave.stdlib.core_api.models.subscriptions.SubscriptionInput(
                    source=self.message.subscription_source
                ),
            ),
        )

        await self.log_event(
            event_name="eave_subscribed",
            event_description="Eave subscribed to a slack message",
            opaque_params={
                "subscription": json.loads(subscription.json()),
            },
        )

        return subscription

    async def notify_existing_subscription(self, subscription: SubscriptionInfo) -> None:
        if subscription.document_reference is not None:
            await self.send_response(
                text=(
                    f"Hey! I'm already watching this conversation and documenting the information <{subscription.document_reference.document_url}|here>. "
                    "Let me know if you need anything else!"
                ),
                eave_message_purpose="notify of existing subscription",
            )
            return

        else:
            # await self.send_response(
            #     text="Hey! I'm currently working on the documentation for this conversation. I'll send an update when it's ready.",
            #     eave_message_purpose="notify of existing subscription",
            # )
            return
