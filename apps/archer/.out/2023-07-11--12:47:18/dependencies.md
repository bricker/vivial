

### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.\n\nOnly consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that. For each dependency that\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects.",
      "role": "system"
    },
    {
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps Infrastructure\n- Eave Development Tools\n- Eave Core Service\n- Eave Slack Integration\n- Eave Jira Integration\n- Eave Github Integration\n- Eave Confluence Integration\n- Eave Marketing Site\n- Eave Service Architecture Tool\n- Eave PubSub Schemas\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\n- OpenAI Service\nFile path: /home/bryan/code/eave/eave-monorepo/apps/slack/eave/slack/brain/core.py\n\npython Code:\n!!!\nclass Brain(IntentProcessingMixin):\n\n    async def process_message(self) -> None:\n        eaveLogger.debug('Brain.process_message', self.eave_ctx)\n        await self.load_data()\n        subscription_response = await self.get_subscription()\n        if subscription_response.subscription:\n            self.subscriptions.append(SubscriptionInfo(subscription=subscription_response.subscription, document_reference=subscription_response.document_reference))\n        i_am_mentioned = await self.message.check_eave_is_mentioned()\n        if i_am_mentioned is True:\n            \"\\n            Eave is mentioned in this message.\\n            1. Acknowledge receipt of the message.\\n            1. If she's being asked for thread information, handle that and stop processing.\\n            1. Otherwise, send a preliminary response and continue processing.\\n            \"\n            await self.acknowledge_receipt()\n            self.message_action = await message_prompts.message_action(context=self.message_context)\n            await self.log_event(event_name='eave_mentioned', event_description='Eave was mentioned in Slack', opaque_params={'action': self.message_action})\n        else:\n            '\\n            Eave is not mentioned in this message.\\n            1. Lookup an existing subscription for this source.\\n            1. If she is not subscribed, then ignore the message and stop processing.\\n            1. Otherwise, continue processing.\\n            '\n            if len(self.subscriptions) == 0:\n                eaveLogger.debug('Eave is not subscribed to this thread; ignoring.', self.eave_ctx)\n                return\n            self.message_action = message_prompts.MessageAction.REFINE_DOCUMENTATION\n        await self.log_event(event_name='slack_eave_action', event_description='Eave is taking an action based on a Slack message', opaque_params={'action': self.message_action})\n        await self.handle_action(message_action=self.message_action)\n\n    async def process_shortcut_event(self) -> None:\n        await self.acknowledge_receipt()\n\n    async def load_data(self) -> None:\n        user_profile = await self.message.get_user_profile()\n        self.user_profile = user_profile\n        expanded_text = await self.message.get_expanded_text()\n        if expanded_text is None:\n            eaveLogger.warning('slack message expanded_text is unexpectedly None', self.eave_ctx, {'message_text': self.message.text})\n            expanded_text = ''\n        self.expanded_text = expanded_text\n        await self.build_message_context()\n!!!",
      "role": "user"
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
  "id": "chatcmpl-7bDeMT5r6l62Z5IDIlUJo3WyfCJYX",
  "object": "chat.completion",
  "created": 1689104962,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"Eave Slack Integration\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 836,
    "completion_tokens": 6,
    "total_tokens": 842
  }
}
```

---

