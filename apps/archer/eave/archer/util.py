from dataclasses import dataclass
import os
import re
import tiktoken
from eave.archer.config import PROJECT_ROOT
import eave.stdlib.openai_client as _o

_ext_to_lang_map = {
    "py": "python",
    "ts": "typescript",
    "js": "javascript",
}

PROMPT_STORE: dict[str, _o.ChatCompletionParameters] = {}

@dataclass
class GithubContext:
    org_name: str
    repo_name: str

def get_lang(filename: str) -> str | None:
    [root, ext] = os.path.splitext(filename)
    return _ext_to_lang_map.get(ext)

def get_filename(filepath: str) -> str:
    return os.path.basename(filepath)

def clean_fpath(path: str) -> str:
    return re.sub(f"^{PROJECT_ROOT}/?", "", path)

def get_file_contents(filepath: str) -> str:
    with open(filepath) as file:
        contents = file.read()

    return contents

def truncate_file_contents_for_model(contents: str, model: _o.OpenAIModel, step: int = 100) -> str:
    encoding = tiktoken.encoding_for_model(model)

    while len(encoding.encode(contents)) > model.max_tokens:
        contents = contents[:-step]

    return contents