

### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of internal APIs. Your task is to find which (if any) of the provided APIs are referenced in the code. Your answer will be used to create a high-level system architecture diagram.\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name. Your full response should be JSON-parseable."
    },
    {
      "role": "user",
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nAPIs:\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\nFile path: /home/bryan/code/eave/eave-monorepo/apps/slack/tests/slack/communication_test.py\n\npython Code:\n!!!\nimport re\n\nfrom slack_sdk.errors import SlackApiError\n\nfrom eave.stdlib.exceptions import HTTPException\nfrom .base import BaseTestCase\n\n\nclass CommunicationMixinTest(BaseTestCase):\n    async def asyncSetUp(self) -> None:\n        await super().asyncSetUp()\n\n    async def test_send_response(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        await self.sut.send_response(\n            text=self.anystring(\"text\"),\n            eave_message_purpose=self.anystring(\"purpose\"),\n            opaque_params=self.anydict(\"params\"),\n        )\n\n        assert mock.call_count == 1\n        assert mock.call_args.kwargs[\"text\"] == f\"<@{self._data_message.user}> {self.getstr('text')}\"\n        assert mock.call_args.kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args.kwargs[\"thread_ts\"] == self.getstr(\"message.thread_ts\")\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_message_purpose\": self.getstr(\"purpose\"),\n                \"eave_message_content\": self.getstr(\"text\"),\n                **self.getdict(\"params\"),\n            },\n        )\n\n    async def test_send_response_no_params(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        await self.sut.send_response(text=self.anystring(\"text\"), eave_message_purpose=self.anystring(\"purpose\"))\n\n        assert mock.call_count == 1\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_message_purpose\": self.getstr(\"purpose\"),\n                \"eave_message_content\": self.getstr(\"text\"),\n            },\n        )\n\n    async def test_notify_failure(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        exc = HTTPException(status_code=500, request_id=self.anystring(\"request id\"))\n        await self.sut.notify_failure(e=exc)\n\n        assert mock.call_count == 1\n        assert re.search(\"technical issue\", mock.call_args.kwargs[\"text\"])\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_request_id\": self.getstr(\"request id\"),\n            },\n        )\n\n    async def test_notify_failure_other_exception(self) -> None:\n        mock = self._data_slack_context.client.chat_postMessage\n        assert mock.call_count == 0\n\n        exc = ValueError(\"test error\")\n        await self.sut.notify_failure(e=exc)\n\n        assert mock.call_count == 1\n        assert re.search(\"technical issue\", mock.call_args.kwargs[\"text\"])\n        assert self.logged_event(\n            event_name=\"eave_sent_message\",\n            opaque_params={\n                \"eave_request_id\": None,\n            },\n        )\n\n    async def test_acknowledge_receipt_with_eave_emoji(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        assert mock.call_count == 0\n\n        await self.sut.acknowledge_receipt()\n\n        assert mock.call_count == 2  # Once for message, once for parent\n        assert mock.call_args_list[0].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[0].kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args_list[0].kwargs[\"timestamp\"] == self.getstr(\"message.ts\")\n\n        assert mock.call_args_list[1].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[1].kwargs[\"channel\"] == self.getstr(\"message.channel\")\n        assert mock.call_args_list[1].kwargs[\"timestamp\"] == self.getstr(\"message.thread_ts\")\n\n        assert self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"eave\",\n            },\n        )\n\n    async def test_acknowledge_receipt_with_no_eave_emoji(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        mock_response = {\"error\": \"invalid_name\"}\n        mock.side_effect = [SlackApiError(message=self.anystring(), response=mock_response), None, None]\n        assert mock.call_count == 0\n\n        await self.sut.acknowledge_receipt()\n\n        assert mock.call_count == 3  # Once for message, second for message re-try, third for parent.\n        assert mock.call_args_list[0].kwargs[\"name\"] == \"eave\"\n        assert mock.call_args_list[1].kwargs[\"name\"] == \"large_purple_circle\"\n\n        assert self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"large_purple_circle\",\n            },\n        )\n\n        assert not self.logged_event(\n            event_name=\"eave_acknowledged_receipt\",\n            opaque_params={\n                \"reaction\": \"eave\",\n            },\n        )\n\n    async def test_acknowledge_receipt_with_some_other_error(self) -> None:\n        mock = self._data_slack_context.client.reactions_add\n        mock_response = {\"error\": self.anystring()}\n        mock.side_effect = SlackApiError(message=self.anystring(), response=mock_response)\n\n        await self.sut.acknowledge_receipt()\n        # error not raised\n\n!!!"
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
  "id": "chatcmpl-7ZOhCtrpdcpknodJCxTXnU7Pb6OoE",
  "object": "chat.completion",
  "created": 1688670766,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"Eave Slack Service\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1353,
    "completion_tokens": 6,
    "total_tokens": 1359
  }
}
```

---

