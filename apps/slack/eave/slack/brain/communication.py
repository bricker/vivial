from typing import Optional

from slack_sdk.errors import SlackApiError
from eave.stdlib.exceptions import HTTPException
from eave.stdlib.typing import JsonObject
from eave.stdlib.logging import eaveLogger

from .base import Base


class CommunicationMixin(Base):
    async def send_response(
        self, text: str, eave_message_purpose: str, opaque_params: Optional[JsonObject] = None
    ) -> None:
        await self.message.send_response(text=text)

        if opaque_params is None:
            opaque_params = {}

        self.log_event(
            event_name="eave_sent_message",
            event_description="Eave sent a message",
            opaque_params={
                "eave_message_content": text,
                "eave_message_purpose": eave_message_purpose,
                **opaque_params,
            },
        )

    async def notify_failure(self, e: Exception) -> None:
        await self.send_response(
            text="I wasn't able to complete the request because of a technical issue. I've let my developers know about it. I can try again if you want, just repeat the request!",
            eave_message_purpose="inform the user of a failure while processing a request",
            opaque_params={
                "request_id": e.request_id if isinstance(e, HTTPException) else None,
            },
        )

    async def acknowledge_receipt(self) -> None:
        try:
            reaction = "eave"
            await self._add_reaction(name=reaction)
        except SlackApiError as e:
            # https://api.slack.com/methods/reactions.add#errors
            error_code = e.response.get("error")
            if error_code == "invalid_name":
                try:
                    # This seems to be available on all Slack workspaces
                    reaction = "large_purple_circle"
                    await self._add_reaction(name=reaction)
                except SlackApiError as e:
                    # Failed twice; give up
                    eaveLogger.warning("unable to react to message, giving up", exc_info=e, extra=self.eave_ctx)
                    return
            else:
                # Error was something else; do nothing.
                # Exception already logged.
                return

        self.log_event(
            event_name="eave_acknowledged_receipt",
            event_description="Eave acknowledged that she received a message",
            opaque_params={
                "reaction": reaction,
            },
        )

    async def _add_reaction(self, name: str) -> None:
        try:
            await self.message.add_reaction(name)
            await self.message.add_reaction_to_parent(name)
        except SlackApiError as e:
            # https://api.slack.com/methods/reactions.add#errors
            error_code = e.response.get("error")
            if error_code == "already_reacted":
                # this is expected sometimes, not a problem.
                return
            elif error_code == "invalid_name":
                eaveLogger.warning(f"reaction {name} doesn't exist in workspace", exc_info=e, extra=self.eave_ctx)
                raise
            else:
                eaveLogger.exception(f"Error reacting to message: {e}", exc_info=e, extra=self.eave_ctx)
                raise