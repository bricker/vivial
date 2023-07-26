import asyncio
import json
import os
from typing import Any
from eave.archer.config import OUTDIR, PROJECT_ROOT, TIMESTAMPF
from eave.archer.fs_hierarchy import FSHierarchy, build_hierarchy

from eave.archer.util import get_file_contents, make_openai_request, truncate_file_contents_for_model
from eave.stdlib.logging import eaveLogger
from eave.stdlib.openai_client import ChatCompletionParameters, ChatMessage, ChatRole, OpenAIModel, formatprompt, get_choice_content

from tree_sitter import Language, Parser

TS_LANG = Language(os.path.join(os.environ["EAVE_HOME"], ".build/tree-sitter/languages.so"), "typescript")

ts_parser = Parser()
ts_parser.set_language(TS_LANG)

_model = OpenAIModel.GPT4

async def _do_request(messages: list[ChatMessage], filepath: str) -> str | None:
    params = ChatCompletionParameters(
        messages=messages,
        model=_model,
        temperature=0,
        presence_penalty=0,
        frequency_penalty=0,
    )

    response = await make_openai_request(filepath=filepath, params=params)
    if not response:
        return None

    answer = get_choice_content(response)
    if not answer:
        return None

    eaveLogger.info(f"{filepath}\n{answer}\n")

    return answer

async def run() -> None:
    hierarchy = build_hierarchy(PROJECT_ROOT)
    tree = await gather_dependencies(hierarchy)

    with open(f"{OUTDIR}/deptree.md", "w") as f:
        f.write("```json\n")
        f.write(json.dumps(tree, indent=2))
        f.write("\n```")

async def gather_dependencies(hierarchy: FSHierarchy) -> dict[str, Any]:
    tree = {}

    for hdir in hierarchy.dirs:
        subtree = await gather_dependencies(hierarchy=hdir)
        tree.update(subtree)

    for filepath in [f for f in hierarchy.files if os.path.basename(f) == "package.json"]:
        file_contents = get_file_contents(filepath, model=OpenAIModel.GPT4)
        if not file_contents:
            continue

        # code = truncate_file_contents_for_model(file_contents=file_contents, prompt="", model=_model)

        package_json = json.loads(file_contents)
        deps = package_json.get("dependencies")
        if not deps:
            continue

        dep_names = deps.keys()
        if len(dep_names) == 0:
            continue

        messages = [
            ChatMessage(role=ChatRole.USER, content=formatprompt(
                f"""
                For each npm package in this list, choose one of the following categories that best describes the package:

                1. internal/private package
                2. third-party service SDK
                3. other
                4. unsure

                Then, group the packages together based on those categories. Then, create a JSON object for the groups with the following keys:

                - "internal_packages" (array of strings)
                - "third_party_sdks" (array of strings)
                - "other" (array of strings)
                - "unsure" (array of strings)

                Output the JSON object and nothing else. Your full response should be valid, parseable JSON.

                Packages: {dep_names}
                """
            )),
        ]

        l1 = await _do_request(messages, filepath=filepath)
        assert l1

        p1 = json.loads(l1)

        tree.update({
            filepath: p1,
        })

    return tree


if __name__ == "__main__":
    asyncio.run(run())
