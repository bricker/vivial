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
- gcr.io/google.com/cloudsdktool/cloud-sdk
File path: /home/bryan/code/eave/eave-monorepo/develop/javascript/_functions.bash

Code:
!!!
if test -z "${_JAVASCRIPT_FUNCTIONS_LOADED:-}"; then
	EAVE_NODE_VERSION=$(cat "${EAVE_HOME}/.node-version")

	function node-validate-version() {
		local current_version
		current_version=$(node --version)
		if ! echo -n "$current_version" | grep -q "v$EAVE_NODE_VERSION"; then
			echo "ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function node-activate-venv() {
		if ! cmd-exists "nvm"; then
			statusmsg -w "automatic environment management is disabled because nvm was not found in your PATH. It is recommended to install nvm."
			return 0
		fi

		local usershell
		usershell=$(shellname)
		case $usershell in
		"fish")
			# This is necessary because `nvm` in Fish might be a function, which can't be used from Bash.
			fish -c "nvm install $EAVE_NODE_VERSION 1>/dev/null 2>&1"
			;;
		*)
			nvm install "$EAVE_NODE_VERSION" 1>/dev/null 2>&1
			;;
		esac
	}

	function node-lint() (
		node-validate-version
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		statusmsg -in "Linting $logtarget (js/ts)"
		npx eslint --max-warnings=0 .

		if test -f "tsconfig.json"; then
			npx tsc --project . --noEmit
		else
			statusmsg -w "No tsconfig.json, skipping TypeScript linting"
		fi
		statusmsg -sp " ✔ "
	)

	function node-format() (
		node-validate-version
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		statusmsg -in "Formatting $logtarget (js/ts)"
		npx eslint . --fix
		statusmsg -sp " ✔ "
	)

	function node-test() (
		node-validate-version
		node-activate-venv

		local target=${1:-tests}
		cd "$target" || exit 1

		npx ava \
			--config="${EAVE_HOME}/develop/javascript/es-config/typescript/ava.config.mjs" .
	)

	_JAVASCRIPT_FUNCTIONS_LOADED=1
fi

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
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps Infrastructure\n- Eave Development Tools\n- Eave Core Service\n- Eave Slack Service\n- Eave Jira Service\n- Eave Github Service\n- Eave Confluence Service\n- Eave Marketing Service\n- Eave Archer Service\n- Eave PubSub Schemas\n- Eave Standard Library (TypeScript)\n- Eave Standard Library (Python)\n- gcr.io/google.com/cloudsdktool/cloud-sdk\nFile path: /home/bryan/code/eave/eave-monorepo/develop/javascript/_functions.bash\n\nCode:\n!!!\nif test -z \"${_JAVASCRIPT_FUNCTIONS_LOADED:-}\"; then\n\tEAVE_NODE_VERSION=$(cat \"${EAVE_HOME}/.node-version\")\n\n\tfunction node-validate-version() {\n\t\tlocal current_version\n\t\tcurrent_version=$(node --version)\n\t\tif ! echo -n \"$current_version\" | grep -q \"v$EAVE_NODE_VERSION\"; then\n\t\t\techo \"ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version\"\n\t\t\texit 1\n\t\tfi\n\t}\n\n\tfunction node-activate-venv() {\n\t\tif ! cmd-exists \"nvm\"; then\n\t\t\tstatusmsg -w \"automatic environment management is disabled because nvm was not found in your PATH. It is recommended to install nvm.\"\n\t\t\treturn 0\n\t\tfi\n\n\t\tlocal usershell\n\t\tusershell=$(shellname)\n\t\tcase $usershell in\n\t\t\"fish\")\n\t\t\t# This is necessary because `nvm` in Fish might be a function, which can't be used from Bash.\n\t\t\tfish -c \"nvm install $EAVE_NODE_VERSION 1>/dev/null 2>&1\"\n\t\t\t;;\n\t\t*)\n\t\t\tnvm install \"$EAVE_NODE_VERSION\" 1>/dev/null 2>&1\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction node-lint() (\n\t\tnode-validate-version\n\t\tnode-activate-venv\n\n\t\tlocal target=$1\n\t\tcd \"$target\" || exit 1\n\t\tlocal logtarget\n\t\tlogtarget=$(^eavepwd)\n\n\t\tstatusmsg -in \"Linting $logtarget (js/ts)\"\n\t\tnpx eslint --max-warnings=0 .\n\n\t\tif test -f \"tsconfig.json\"; then\n\t\t\tnpx tsc --project . --noEmit\n\t\telse\n\t\t\tstatusmsg -w \"No tsconfig.json, skipping TypeScript linting\"\n\t\tfi\n\t\tstatusmsg -sp \" \u2714 \"\n\t)\n\n\tfunction node-format() (\n\t\tnode-validate-version\n\t\tnode-activate-venv\n\n\t\tlocal target=$1\n\t\tcd \"$target\" || exit 1\n\t\tlocal logtarget\n\t\tlogtarget=$(^eavepwd)\n\n\t\tstatusmsg -in \"Formatting $logtarget (js/ts)\"\n\t\tnpx eslint . --fix\n\t\tstatusmsg -sp \" \u2714 \"\n\t)\n\n\tfunction node-test() (\n\t\tnode-validate-version\n\t\tnode-activate-venv\n\n\t\tlocal target=${1:-tests}\n\t\tcd \"$target\" || exit 1\n\n\t\tnpx ava \\\n\t\t\t--config=\"${EAVE_HOME}/develop/javascript/es-config/typescript/ava.config.mjs\" .\n\t)\n\n\t_JAVASCRIPT_FUNCTIONS_LOADED=1\nfi\n\n!!!",
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
  "id": "chatcmpl-7bFc3KUCYPV2CKE99DKsGVCTXpKVr",
  "object": "chat.completion",
  "created": 1689112507,
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
    "prompt_tokens": 915,
    "completion_tokens": 1,
    "total_tokens": 916
  }
}
```

