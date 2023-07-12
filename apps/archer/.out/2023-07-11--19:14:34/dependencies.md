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
- gcr.io/google.com/cloudsdktool/cloud-sdk
- Cloud SQL
File path: /home/bryan/code/eave/eave-monorepo/apps/core/eave/core/internal/oauth/google.py

python Code:
!!!
import typing
from dataclasses import dataclass

import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import googleapiclient.discovery

from eave.core.internal.config import app_config
from eave.stdlib.typing import JsonObject
from eave.stdlib.util import erasetype

from .models import OAuthFlowInfo

_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

_REDIRECT_URI = f"{app_config.eave_public_api_base}/oauth/google/callback"


class GoogleIdToken:
    """
    https://developers.google.com/identity/openid-connect/openid-connect#authenticatingtheuser
    """

    sub: str
    """Google globally unique and immutable user ID"""
    given_name: typing.Optional[str]
    email: typing.Optional[str]

    def __init__(self, data: JsonObject) -> None:
        self.sub = erasetype(data, "sub", "")
        self.given_name = erasetype(data, "given_name")
        self.email = erasetype(data, "email")


@dataclass
class GoogleOAuthClientConfig:
    """Documentation for the Google Client Config doc format"""

    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: typing.List[str]


@dataclass
class GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.userinfo.html#get
    """

    email: typing.Optional[str] = None  # The user's email address.
    family_name: typing.Optional[str] = None  # The user's last name.
    gender: typing.Optional[str] = None  # The user's gender.
    given_name: typing.Optional[str] = None  # The user's first name.
    hd: typing.Optional[str] = None  # The hosted domain e.g. example.com if the user is Google apps user.
    id: typing.Optional[str] = None  # The obfuscated ID of the user.
    link: typing.Optional[str] = None  # URL of the profile page.
    locale: typing.Optional[str] = None  # The user's preferred locale.
    name: typing.Optional[str] = None  # The user's full name.
    picture: typing.Optional[str] = None  # URL of the user's picture image.
    verified_email: typing.Optional[
        bool
    ] = None  # Boolean flag which is true if the email address is verified. Always verified because we only return the user's primary email address.


def get_userinfo(credentials: google.oauth2.credentials.Credentials) -> GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.html
    """
    with googleapiclient.discovery.build("oauth2", "v2", credentials=credentials) as service:
        user_info = service.userinfo().get().execute()

    return GoogleOAuthV2GetResponse(**user_info)


def get_oauth_credentials(access_token: str, refresh_token: str) -> google.oauth2.credentials.Credentials:
    google_oauth_client_config = app_config.eave_google_oauth_client_credentials
    creds = google_oauth_client_config["web"]
    token_uri = creds["token_uri"]
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]

    credentials = google.oauth2.credentials.Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=_OAUTH_SCOPES,
    )
    return credentials


def build_flow(state: typing.Optional[str] = None) -> google_auth_oauthlib.flow.Flow:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        app_config.eave_google_oauth_client_credentials,
        scopes=_OAUTH_SCOPES,
        redirect_uri=_REDIRECT_URI,
        state=state,
    )

    return flow


def get_oauth_flow_info() -> OAuthFlowInfo:
    """
    https://developers.google.com/identity/protocols/oauth2/web-server#python_1
    """
    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",  # forces the consent screen to make sure we get a refresh token
        include_granted_scopes="true",
    )

    return OAuthFlowInfo(authorization_url=authorization_url, state=state)


def decode_id_token(id_token: str) -> GoogleIdToken:
    token_json = google.oauth2.id_token.verify_oauth2_token(
        id_token=id_token,
        audience=app_config.eave_google_oauth_client_id,
        request=google.auth.transport.requests.Request(),
    )

    # TODO: Verify nonce
    token = GoogleIdToken(data=token_json)
    return token

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
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps Infrastructure\n- Eave Development Tools\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\n- Eave PubSub Schemas\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\n- gcr.io/google.com/cloudsdktool/cloud-sdk\n- Cloud SQL\nFile path: /home/bryan/code/eave/eave-monorepo/apps/core/eave/core/internal/oauth/google.py\n\npython Code:\n!!!\nimport typing\nfrom dataclasses import dataclass\n\nimport google.auth.transport.requests\nimport google.oauth2.credentials\nimport google.oauth2.id_token\nimport google_auth_oauthlib.flow\nimport googleapiclient.discovery\n\nfrom eave.core.internal.config import app_config\nfrom eave.stdlib.typing import JsonObject\nfrom eave.stdlib.util import erasetype\n\nfrom .models import OAuthFlowInfo\n\n_OAUTH_SCOPES = [\n    \"https://www.googleapis.com/auth/userinfo.email\",\n    \"https://www.googleapis.com/auth/userinfo.profile\",\n    \"openid\",\n]\n\n_REDIRECT_URI = f\"{app_config.eave_public_api_base}/oauth/google/callback\"\n\n\nclass GoogleIdToken:\n    \"\"\"\n    https://developers.google.com/identity/openid-connect/openid-connect#authenticatingtheuser\n    \"\"\"\n\n    sub: str\n    \"\"\"Google globally unique and immutable user ID\"\"\"\n    given_name: typing.Optional[str]\n    email: typing.Optional[str]\n\n    def __init__(self, data: JsonObject) -> None:\n        self.sub = erasetype(data, \"sub\", \"\")\n        self.given_name = erasetype(data, \"given_name\")\n        self.email = erasetype(data, \"email\")\n\n\n@dataclass\nclass GoogleOAuthClientConfig:\n    \"\"\"Documentation for the Google Client Config doc format\"\"\"\n\n    client_id: str\n    project_id: str\n    auth_uri: str\n    token_uri: str\n    auth_provider_x509_cert_url: str\n    client_secret: str\n    redirect_uris: typing.List[str]\n\n\n@dataclass\nclass GoogleOAuthV2GetResponse:\n    \"\"\"\n    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.userinfo.html#get\n    \"\"\"\n\n    email: typing.Optional[str] = None  # The user's email address.\n    family_name: typing.Optional[str] = None  # The user's last name.\n    gender: typing.Optional[str] = None  # The user's gender.\n    given_name: typing.Optional[str] = None  # The user's first name.\n    hd: typing.Optional[str] = None  # The hosted domain e.g. example.com if the user is Google apps user.\n    id: typing.Optional[str] = None  # The obfuscated ID of the user.\n    link: typing.Optional[str] = None  # URL of the profile page.\n    locale: typing.Optional[str] = None  # The user's preferred locale.\n    name: typing.Optional[str] = None  # The user's full name.\n    picture: typing.Optional[str] = None  # URL of the user's picture image.\n    verified_email: typing.Optional[\n        bool\n    ] = None  # Boolean flag which is true if the email address is verified. Always verified because we only return the user's primary email address.\n\n\ndef get_userinfo(credentials: google.oauth2.credentials.Credentials) -> GoogleOAuthV2GetResponse:\n    \"\"\"\n    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.html\n    \"\"\"\n    with googleapiclient.discovery.build(\"oauth2\", \"v2\", credentials=credentials) as service:\n        user_info = service.userinfo().get().execute()\n\n    return GoogleOAuthV2GetResponse(**user_info)\n\n\ndef get_oauth_credentials(access_token: str, refresh_token: str) -> google.oauth2.credentials.Credentials:\n    google_oauth_client_config = app_config.eave_google_oauth_client_credentials\n    creds = google_oauth_client_config[\"web\"]\n    token_uri = creds[\"token_uri\"]\n    client_id = creds[\"client_id\"]\n    client_secret = creds[\"client_secret\"]\n\n    credentials = google.oauth2.credentials.Credentials(\n        token=access_token,\n        refresh_token=refresh_token,\n        token_uri=token_uri,\n        client_id=client_id,\n        client_secret=client_secret,\n        scopes=_OAUTH_SCOPES,\n    )\n    return credentials\n\n\ndef build_flow(state: typing.Optional[str] = None) -> google_auth_oauthlib.flow.Flow:\n    flow = google_auth_oauthlib.flow.Flow.from_client_config(\n        app_config.eave_google_oauth_client_credentials,\n        scopes=_OAUTH_SCOPES,\n        redirect_uri=_REDIRECT_URI,\n        state=state,\n    )\n\n    return flow\n\n\ndef get_oauth_flow_info() -> OAuthFlowInfo:\n    \"\"\"\n    https://developers.google.com/identity/protocols/oauth2/web-server#python_1\n    \"\"\"\n    flow = build_flow()\n\n    authorization_url, state = flow.authorization_url(\n        access_type=\"offline\",\n        prompt=\"consent\",  # forces the consent screen to make sure we get a refresh token\n        include_granted_scopes=\"true\",\n    )\n\n    return OAuthFlowInfo(authorization_url=authorization_url, state=state)\n\n\ndef decode_id_token(id_token: str) -> GoogleIdToken:\n    token_json = google.oauth2.id_token.verify_oauth2_token(\n        id_token=id_token,\n        audience=app_config.eave_google_oauth_client_id,\n        request=google.auth.transport.requests.Request(),\n    )\n\n    # TODO: Verify nonce\n    token = GoogleIdToken(data=token_json)\n    return token\n\n!!!",
      "role": "user"
    }
  ],
  "frequency_penalty": -0.5,
  "presence_penalty": -0.5,
  "top_p": 0.1,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

### Response

```json
{
  "id": "chatcmpl-7bJkp53CJqW9qBQUN18wYpgPDijPi",
  "object": "chat.completion",
  "created": 1689128427,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"gcr.io/google.com/cloudsdktool/cloud-sdk\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1411,
    "completion_tokens": 12,
    "total_tokens": 1423
  }
}
```

