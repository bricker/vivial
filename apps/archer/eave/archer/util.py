import ast
from dataclasses import dataclass
import os
import re
from typing import Any, Tuple
from openai.openai_object import OpenAIObject
import tiktoken
from .config import CONTENT_EXCLUDES
import eave.stdlib.openai_client as _o

# TODO: Use https://github.com/github-linguist/linguist/blob/master/lib/linguist/languages.yml
_ext_to_lang_map = {
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
}

PROMPT_STORE: dict[str, Any] = {}

TOTAL_TOKENS = {
    "prompt": 0,
    "completion": 0,
    "total": 0,
}

SHARED_JSON_OUTPUT_INSTRUCTIONS = "Your response will be passed unmodified into a JSON parser, so your full response should be a valid, parseable, compact JSON document."

@dataclass
class GithubContext:
    org_name: str
    repo_name: str

def get_lang(filename: str) -> str | None:
    [root, ext] = os.path.splitext(filename)
    return _ext_to_lang_map.get(ext)

def get_filename(filepath: str) -> str:
    return os.path.basename(filepath)

def clean_fpath(path: str, prefix: str = "") -> str:
    return re.sub(f"^{prefix}/?", "", path)

def get_file_contents(filepath: str, model: _o.OpenAIModel, strip_imports: bool = True) -> str | None:
    if any([re.search(e, filepath) for e in CONTENT_EXCLUDES]):
        print(filepath, "Skipping file due to content exclude.")
        return None

    with open(filepath) as file:
        contents = file.read()

    # file_contents = remove_imports(filepath=filepath, contents=file_contents)
    filelen = len(contents)
    print(filepath, f"filelen={filelen}", f"tokenlen={len(get_tokens(contents, model=model))}")

    if len(contents.strip()) == 0:
        return None

    return contents

def remove_imports(filepath: str, contents: str) -> str:
    lang = get_lang(filepath)
    match lang:
        case "python":
            tree = ast.parse(contents)
            tree.body = [node for node in tree.body if not isinstance(node, ast.ImportFrom) and not isinstance(node, ast.Import)]
            return ast.unparse(tree)
        case _:
            return contents

def get_tokens(content: str, model: _o.OpenAIModel) -> list[int]:
    encoding = tiktoken.encoding_for_model(model)
    return encoding.encode(content)

def truncate_file_contents_for_model(file_contents: str, prompt: str, model: _o.OpenAIModel, step: int = 100) -> str:
    while len(get_tokens(prompt + file_contents, model=model)) > model.max_tokens:
        file_contents = file_contents[:-step]

    return file_contents

def make_prompt_content(messages: list[str]) -> str:
    stripped = [m for m in messages if m]
    return "\n".join(stripped)

async def make_openai_request(filepath: str, params: _o.ChatCompletionParameters) -> OpenAIObject | None:
    try:
        response = await _o.chat_completion_full_response(params, baseTimeoutSeconds=10)
        assert response
        print(filepath, "response=", response)
        TOTAL_TOKENS["prompt"] += response["usage"]["prompt_tokens"]
        TOTAL_TOKENS["completion"] += response["usage"]["completion_tokens"]
        TOTAL_TOKENS["total"] += response["usage"]["total_tokens"]
        return response
    except _o.MaxRetryAttemptsReachedError:
        print(filepath, "WARNING: Max retry attempts reached")
        return None
    except TimeoutError:
        print(filepath, "WARNING: Timeout")
        return None
