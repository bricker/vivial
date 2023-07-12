### Prompt

```
SYSTEM:
You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.

Only consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that. For each dependency that

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
File path: /home/bryan/code/eave/eave-monorepo/apps/core/eave_alembic/script.py.mako

Code:
!!!
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

!!!
```

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
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps Infrastructure\n- Eave Development Tools\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\n- Eave PubSub Schemas\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\n- Google Cloud KMS\n- Cloud SQL\nFile path: /home/bryan/code/eave/eave-monorepo/apps/core/eave_alembic/script.py.mako\n\nCode:\n!!!\n\"\"\"${message}\n\nRevision ID: ${up_revision}\nRevises: ${down_revision | comma,n}\nCreate Date: ${create_date}\n\n\"\"\"\nfrom alembic import op\nimport sqlalchemy as sa\n${imports if imports else \"\"}\n\n# revision identifiers, used by Alembic.\nrevision = ${repr(up_revision)}\ndown_revision = ${repr(down_revision)}\nbranch_labels = ${repr(branch_labels)}\ndepends_on = ${repr(depends_on)}\n\n\ndef upgrade() -> None:\n    ${upgrades if upgrades else \"pass\"}\n\n\ndef downgrade() -> None:\n    ${downgrades if downgrades else \"pass\"}\n\n!!!",
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

### Response

```json
{
  "id": "chatcmpl-7bIv8Ymy4AbXck6MvIX1smeGKcOCm",
  "object": "chat.completion",
  "created": 1689125222,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 473,
    "completion_tokens": 1,
    "total_tokens": 474
  }
}
```

