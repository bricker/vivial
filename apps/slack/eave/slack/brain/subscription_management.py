from eave.slack.brain.communication import CommunicationMixin
import eave.stdlib.core_api.client
import eave.stdlib.core_api.operations
import eave.stdlib.core_api.enums
import eave.stdlib.analytics as eave_analytics
from .base import Base
from . import message_prompts

class SubscriptionManagementMixin(CommunicationMixin):
    async def get_subscription(self) -> eave.stdlib.core_api.operations.GetSubscription.ResponseBody | None:
        subscription = await eave.stdlib.core_api.client.get_subscription(
            team_id=self.eave_team.id,
            input=eave.stdlib.core_api.operations.GetSubscription.RequestBody(
                subscription=eave.stdlib.core_api.operations.SubscriptionInput(source=self.message.subscription_source),
            ),
        )
        return subscription

    async def create_subscription(self) -> eave.stdlib.core_api.operations.CreateSubscription.ResponseBody:
        """
        Gets and returns the subscription if it already exists, otherwise creates and returns a new subscription.
        """
        subscription = await eave.stdlib.core_api.client.create_subscription(
            team_id=self.eave_team.id,
            input=eave.stdlib.core_api.operations.CreateSubscription.RequestBody(
                subscription=eave.stdlib.core_api.operations.SubscriptionInput(source=self.message.subscription_source),
            ),
        )

        self.log_event(
            event_name="eave_subscribed",
            event_description="Eave subscribed to a slack message",
            opaque_params={
                "subscription": subscription.dict(),
            }
        )

        return subscription


    async def notify_existing_subscription(self, subscription: eave.stdlib.core_api.operations.GetSubscription.ResponseBody) -> None:
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
            await self.send_response(
                text="Hey! I'm currently working on the documentation for this conversation. I'll send an update when it's ready.",
                eave_message_purpose="notify of existing subscription",
            )
            return
