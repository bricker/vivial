import os
import tiktoken
import eave.stdlib.openai_client as _o

_ext_to_lang_map = {
    "py": "python",
    "ts": "typescript",
    "js": "javascript",
}

def get_lang(filename: str) -> str | None:
    [root, ext] = os.path.splitext(filename)
    return _ext_to_lang_map.get(ext)

def get_filename(filepath: str) -> str:
    return os.path.basename(filepath)

def get_file_contents(filepath: str) -> str:
    with open(filepath) as file:
        contents = file.read()

    return contents

def truncate_file_contents_for_model(contents: str, model: _o.OpenAIModel, step: int = 100) -> str:
    encoding = tiktoken.encoding_for_model(model)

    while len(encoding.encode(contents)) > model.max_tokens:
        contents = contents[:-step]

    return contents