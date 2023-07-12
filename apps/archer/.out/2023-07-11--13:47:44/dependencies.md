

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
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps\n- Eave Core\n- Eave Slack\n- Eave Jira\n- Eave GitHub\n- Eave Confluence\n- Eave Marketing\n- Eave Archer\n- Eave PubSub Schemas\n- Eave Standard Library (Python)\n- Eave Standard Library (TypeScript)\n- hashicorp/google\nFile path: /home/bryan/code/eave/eave-monorepo/terraform/eavefyi-dev/project.tf\n\nCode:\n!!!\nresource \"google_project\" \"eavefyi-dev\" {\n  auto_create_network = true\n  billing_account     = \"013F5E-137CB0-B6AA2A\"\n  folder_id           = null\n  labels              = {}\n  name                = \"eavefyi-dev\"\n  org_id              = \"482990375115\"\n  project_id          = \"eavefyi-dev\"\n  skip_delete         = null\n  timeouts {\n    create = null\n    delete = null\n    read   = null\n    update = null\n  }\n}\n\n!!!",
      "role": "user"
    }
  ],
  "frequency_penalty": -1,
  "presence_penalty": -1,
  "temperature": 0,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

#### Response

```json
{
  "id": "chatcmpl-7bEa0EXRpMOrbVMFuc3iVAarw5Qgn",
  "object": "chat.completion",
  "created": 1689108536,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"hashicorp/google\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 446,
    "completion_tokens": 6,
    "total_tokens": 452
  }
}
```

---

