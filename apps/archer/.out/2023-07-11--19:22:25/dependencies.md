### Prompt

```
SYSTEM:
You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.

Only consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that.

Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects.
```

```
USER:
GitHub organization: eave-fyi

Repository: eave-monorepo

Known services:
- Eave DevOps Infrastructure
- Eave Development Tools
- Eave Core Service
- Eave Slack Service
- Eave Jira Service
- Eave Github Service
- Eave Confluence Service
- Eave Marketing Service
- Eave Archer Service
- Eave PubSub Schemas
- Eave Standard Library (TypeScript)
- Eave Standard Library (Python)
- Google Cloud KMS
- Cloud SQL
- OpenAI
- Redis
- Eave Atlassian Service
- Google Drive
File path: /home/bryan/code/eave/eave-monorepo/libs/eave-stdlib-py/src/eave/stdlib/github_api/models.py

python Code:
!!!
import pydantic


# Source response object defined in Github API
# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class GithubRepository(pydantic.BaseModel):
    node_id: str
    full_name: str

!!!
```

### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.\n\nOnly consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that.\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects.",
      "role": "system"
    },
    {
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps Infrastructure\n- Eave Development Tools\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\n- Eave PubSub Schemas\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\n- Google Cloud KMS\n- Cloud SQL\n- OpenAI\n- Redis\n- Eave Atlassian Service\n- Google Drive\nFile path: /home/bryan/code/eave/eave-monorepo/libs/eave-stdlib-py/src/eave/stdlib/github_api/models.py\n\npython Code:\n!!!\nimport pydantic\n\n\n# Source response object defined in Github API\n# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository\nclass GithubRepository(pydantic.BaseModel):\n    node_id: str\n    full_name: str\n\n!!!",
      "role": "user"
    }
  ],
  "frequency_penalty": -0.1,
  "presence_penalty": -0.1,
  "top_p": 0.1,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

### Response

```json
{
  "id": "chatcmpl-7bK8s85kB4TXUK2Rbq9UhMAOTUWY9",
  "object": "chat.completion",
  "created": 1689129918,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"Eave Github Service\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 425,
    "completion_tokens": 6,
    "total_tokens": 431
  }
}
```

