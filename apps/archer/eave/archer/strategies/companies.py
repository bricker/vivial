import asyncio
from io import TextIOWrapper
import json
import os
import re
from textwrap import dedent
from typing import Any, Tuple
from eave.archer.config import MODEL, OUTDIR, PROJECT_ROOT, TIMESTAMPF
from eave.archer.fs_hierarchy import FSHierarchy, build_hierarchy

from eave.archer.util import clean_fpath, get_file_contents, make_openai_request, truncate_file_contents_for_model
from eave.stdlib.logging import eaveLogger
from eave.stdlib.openai_client import ChatCompletionParameters, ChatMessage, ChatRole, OpenAIModel, formatprompt, get_choice_content

async def _do_request(messages: list[ChatMessage], **kwargs: Any) -> str | None:
    params = ChatCompletionParameters(
        messages=messages,
        model=MODEL,
        **kwargs,
    )

    await asyncio.sleep(2)

    response = await make_openai_request(params=params)
    if not response:
        return None

    answer = get_choice_content(response)
    if not answer:
        return None

    eaveLogger.info(f"{answer}\n")
    return answer

async def run() -> None:
    print("Strategy: rolling_summaries")
    hierarchy = build_hierarchy(f"{PROJECT_ROOT}/apps/slack")
    fp = open(".out/rolling_summaries.md", "w")
    await gather_summaries(hierarchy, fp)
    fp.close()

    fp = open(".out/graph-gen.dot", "w")
    fp.write(dedent("""
    digraph {
        "Eave Slack App"
    """))

    for line in write_graph(hierarchy, fp):
        fp.write(f"    {line}\n")

    fp.write("}\n")
    fp.close()

def gather_connections(hierarchy: FSHierarchy) -> Tuple[set[str], set[str]]:
    external_connections: set[str] = set()
    internal_connections: set[str] = set()

    for file in hierarchy.files:
        external_connections.update(file.external_service_references)
        internal_connections.update(file.internal_service_references)

    for dir in hierarchy.dirs:
        cext, cint = gather_connections(dir)
        external_connections.update(cext)
        internal_connections.update(cint)

    return external_connections, internal_connections

def write_connections(hierarchy: FSHierarchy, fp: TextIOWrapper) -> set[str]:
    lines = set[str]()

    # if not hierarchy.service_name:
    #     return lines

    # lines.add(f"\"{hierarchy.service_name}\"")

    cext, cint = gather_connections(hierarchy)

    for conn in cext:
        if hierarchy.service_name != conn:
            # fp.write(f"  {conn}\n")
            # lines.add(f"\"{hierarchy.service_name}\" -> \"{conn}\"")
            lines.add(f"\"Eave Slack App\" -> \"{conn}\"")

    # for conn in cint:
    #     if hierarchy.service_name != conn:
    #         # fp.write(f"  {conn}\n")
    #         lines.add(f"\"{hierarchy.service_name}\" -> \"{conn}\"")

    return lines

def write_graph(hierarchy: FSHierarchy, fp: TextIOWrapper) -> set[str]:
    lines = set[str]()
    lines.update(write_connections(hierarchy, fp))

    for dir in hierarchy.dirs:
        lines.update(write_graph(dir, fp))

    return lines

async def gather_summaries(hierarchy: FSHierarchy, fp: TextIOWrapper) -> None:
    for fileref in [f for f in hierarchy.files]:
        print("filepath=", fileref.clean_path)

        file_contents = fileref.read_file()
        if not file_contents:
            continue

        fp.write(f"## {fileref.clean_path}\n\n")

        # prompt_prefix = formatprompt(
        #     f"""
        #     This is code from a file called {fileref.clean_path}. Summarize the code. Note if this file starts an application server, such as Express, Flake, Django, Gin, Rack, etc.:

        #     ===
        #     """)

        # code = truncate_file_contents_for_model(file_contents=file_contents, prompt=prompt_prefix, model=MODEL)

        # messages = [
        #     ChatMessage(role=ChatRole.USER, content=formatprompt(
        #         prompt_prefix,
        #         code,
        #         "===",
        #     )),
        # ]

        # l1 = await _do_request(messages, temperature=0.2, frequency_penalty=0.1)
        # assert l1

        # fileref.summary = l1
        # fp.write(f"```\n{fileref.summary}\n```\n\n")

        messages = [
            ChatMessage(role=ChatRole.USER, content=formatprompt(
                """
                Does this code reference any known SaaS or PaaS companies? If so, which ones?
                Output your response as a JSON array of strings. If there are no references, return an empty JSON array. Your full response should be valid, parseable JSON.
                ===
                """,
                file_contents,
                """
                ===
                """,
            )),
        ]

        l1 = await _do_request(messages)
        assert l1

        fileref.external_service_references.extend([_normalize(s) for s in json.loads(l1)])
        fp.write(f"```json\n{json.dumps(fileref.external_service_references, indent=2)}\n```\n\n")
        fp.flush()

        # messages = [
        #     ChatMessage(role=ChatRole.USER, content=formatprompt(
        #         """
        #         Does this file summary reference any internal services or APIs? If so, which ones? Exclude things like built-in libraries or API frameworks. Exclude APIs or services that are likely to be external to the Eave organization. Create a name for each service. The names should exclude mentions of HTTP libraries or API frameworks like Starlette, Express, Gin, or Rack.

        #         Then, simplify and normalize the names of the services. For example:

        #         - "Confluence App" instead of "Eave Confluence Server"
        #         - "Slack App" instead of "Eave Slack App" or "Starlette Slack App"

        #         Output your response as a JSON array of strings. If there are no references, return an empty JSON array. Your full response should be valid, parseable JSON.
        #         ===
        #         """,
        #         fileref.summary,
        #         """
        #         ===
        #         """,
        #     )),
        # ]

        # l1 = await _do_request(messages)
        # assert l1

        # fileref.internal_service_references.extend([_normalize(s) for s in json.loads(l1)])
        # fp.write(f"```json\n{json.dumps(fileref.internal_service_references, indent=2)}\n```\n\n")
        # fp.flush()


    for hdir in hierarchy.dirs:
        await gather_summaries(hierarchy=hdir, fp=fp)
        if hdir.service_name:
            pass

    # summary_list = []

    # for file in [x for x in hierarchy.files if x.summary]:
    #     summary_list.append(f"### File: {file.clean_path}\n\n{file.summary}")

    # for hdir in [x for x in hierarchy.dirs if x.summary]:
    #     summary_list.append(f"### Directory: {hdir.clean_path}\n\n{hdir.summary}")

    # if len(summary_list) > 0:
    #     dirsum = "\n\n".join(summary_list)

    #     messages = [
    #         ChatMessage(role=ChatRole.USER, content=formatprompt(
    #             f"""
    #             This is a list of names and summaries of the source code files in a directory{', and the names and summaries of its sub-directories' if len(hierarchy.dirs) > 0 else ''}. Decide if this directory contains a file that starts an application server. Then, if there is exactly one application server in this directory, create a short name (1-3 words) for the application. Otherwise, do not create a name.

    #             If you created a name for the application, respond with that name and nothing else. Otherwise, respond with the word "SENTINEL" and nothing else.

    #             ===
    #             """,
    #             dirsum,
    #             "===",
    #         )),
    #     ]

    #     l1 = await _do_request(messages, temperature=0, frequency_penalty=0)
    #     assert l1

    #     l1 = _normalize(l1)
    #     fp.write(f"## {hierarchy.clean_path}\n\n")
    #     fp.write("```\n")
    #     fp.write(f"{l1}\n")
    #     fp.write("```\n\n")

    #     if l1 != "sentinel":
    #         hierarchy.service_name = l1

    fp.flush()

def _normalize(string: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", string).lower()

if __name__ == "__main__":
    asyncio.run(run())
