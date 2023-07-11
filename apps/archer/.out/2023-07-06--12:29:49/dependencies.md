

### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of internal APIs. Your task is to find which (if any) of the provided APIs are referenced in the code. Your answer will be used to create a high-level system architecture diagram.\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects."
    },
    {
      "role": "user",
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nAPIs:\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\nFile path: /home/bryan/code/eave/eave-monorepo/apps/slack/eave/slack/brain/core.py\n\npython Code:\n!!!\nfrom eave.stdlib.core_api.models.subscriptions import SubscriptionInfo\nfrom . import message_prompts\n\n\nfrom eave.stdlib.logging import eaveLogger\nfrom .intent_processing import IntentProcessingMixin\n\n\nclass Brain(IntentProcessingMixin):\n    async def process_message(self) -> None:\n        eaveLogger.debug(\"Brain.process_message\", self.eave_ctx)\n\n        await self.load_data()\n\n        subscription_response = await self.get_subscription()\n        if subscription_response.subscription:\n            self.subscriptions.append(\n                SubscriptionInfo(\n                    subscription=subscription_response.subscription,\n                    document_reference=subscription_response.document_reference,\n                )\n            )\n\n        i_am_mentioned = await self.message.check_eave_is_mentioned()\n        if i_am_mentioned is True:\n            \"\"\"\n            Eave is mentioned in this message.\n            1. Acknowledge receipt of the message.\n            1. If she's being asked for thread information, handle that and stop processing.\n            1. Otherwise, send a preliminary response and continue processing.\n            \"\"\"\n            await self.acknowledge_receipt()\n\n            self.message_action = await message_prompts.message_action(context=self.message_context)\n\n            self.log_event(\n                event_name=\"eave_mentioned\",\n                event_description=\"Eave was mentioned in Slack\",\n                opaque_params={\n                    \"action\": self.message_action,\n                },\n            )\n\n        else:\n            \"\"\"\n            Eave is not mentioned in this message.\n            1. Lookup an existing subscription for this source.\n            1. If she is not subscribed, then ignore the message and stop processing.\n            1. Otherwise, continue processing.\n            \"\"\"\n            if len(self.subscriptions) == 0:\n                eaveLogger.debug(\"Eave is not subscribed to this thread; ignoring.\", self.eave_ctx)\n                return\n\n            self.message_action = message_prompts.MessageAction.REFINE_DOCUMENTATION\n\n        self.log_event(\n            event_name=\"slack_eave_action\",\n            event_description=\"Eave is taking an action based on a Slack message\",\n            opaque_params={\n                \"action\": self.message_action,\n            },\n        )\n\n        await self.handle_action(message_action=self.message_action)\n\n    async def process_shortcut_event(self) -> None:\n        await self.acknowledge_receipt()\n\n        # source = eave_models.SubscriptionSource(\n        #     event=eave_models.SubscriptionSourceEvent.slack_message,\n        #     id=message.subscription_id,\n        # )\n\n        # response = await eave_models.client.get_or_create_subscription(source=source)\n        # manager = DocumentManager(message=message, subscription=response.subscription)\n        # await manager.process_message()\n\n    async def load_data(self) -> None:\n        user_profile = await self.message.get_user_profile()\n        self.user_profile = user_profile\n\n        expanded_text = await self.message.get_expanded_text()\n        if expanded_text is None:\n            eaveLogger.warning(\n                \"slack message expanded_text is unexpectedly None\",\n                self.eave_ctx,\n                {\"message_text\": self.message.text},\n            )\n\n            # FIXME: Brain should allow None expanded_text so it can retry.\n            expanded_text = \"\"\n\n        self.expanded_text = expanded_text\n\n        await self.build_message_context()\n\n!!!"
    }
  ],
  "temperature": 0,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

#### Response

```json
{
  "id": "chatcmpl-7ZOzEcRcHh1F6XRSHns3AHzTuETfh",
  "object": "chat.completion",
  "created": 1688671884,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"Eave Core Service\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 878,
    "completion_tokens": 6,
    "total_tokens": 884
  }
}
```

---

