import ast
from dataclasses import dataclass
import os
import re
from typing import Any, Tuple
import tiktoken
import eave.stdlib.openai_client as _o

# TODO: Use https://github.com/github-linguist/linguist/blob/master/lib/linguist/languages.yml
_ext_to_lang_map = {
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
}

PROMPT_STORE: dict[str, Tuple[Any, Any]] = {}
TOTAL_TOKENS = {
    "prompt": 0,
    "completion": 0,
    "total": 0,
}

SHARED_JSON_OUTPUT_INSTRUCTIONS = "Your full response should be JSON-parseable, with no indentation or newlines between objects."

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

def get_file_contents(filepath: str, strip_imports: bool = True) -> str:
    with open(filepath) as file:
        contents = file.read()

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