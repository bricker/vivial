import asyncio
import datetime
from io import TextIOWrapper
import json
import jsonpickle
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
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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

    hierarchy_path = ".out/hierarchy.json"
    
    if os.path.isfile(hierarchy_path):
        with open(hierarchy_path, "r") as file:
            serialized_hierarchy = file.read()
        hierarchy = jsonpickle.decode(serialized_hierarchy)
    else:
        hierarchy = build_hierarchy(f"{PROJECT_ROOT}/apps")
        fp = open(".out/rolling_summaries.md", "w")
        await gather_summaries(hierarchy, fp)
        fp.close()

        # Save the hierarchy object to a file
        serialized_hierarchy = jsonpickle.encode(hierarchy)
        with open(hierarchy_path, "w") as file:
            file.write(serialized_hierarchy) # type: ignore

    fp = open(".out/graph-gen.dot", "w")
    fp.write(dedent("""
    digraph {
    """))

    for line in write_graph(hierarchy, fp):
        fp.write(f"    {line}\n")

    fp.write("}\n")
    fp.close()

def gather_connections(hierarchy: FSHierarchy) -> set[str]:
    connections: set[str] = set()

    for file in hierarchy.files:
        connections.update(file.service_references)

    for dir in hierarchy.dirs:
        c = gather_connections(dir)
        connections.update(c)

    return connections

def write_connections(hierarchy: FSHierarchy, fp: TextIOWrapper) -> set[str]:
    lines = set[str]()

    if not hierarchy.service_name:
        return lines

    lines.add(f"\"{hierarchy.service_name}\"")

    connections = gather_connections(hierarchy)

    for conn in connections:
        if hierarchy.service_name != conn:
            # fp.write(f"  {conn}\n")
            lines.add(f"\"{hierarchy.service_name}\" -> \"{conn}\"")

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

        prompt_prefix = formatprompt(
            f"""
            This is code from a file called {fileref.clean_path}. Summarize the code. Note if this file starts an application server, such as Express, Flake, Django, Gin, Rack, etc.:

            ===
            """)

        code = truncate_file_contents_for_model(file_contents=file_contents, prompt=prompt_prefix, model=MODEL)

        messages = [
            ChatMessage(role=ChatRole.USER, content=formatprompt(
                prompt_prefix,
                code,
                "===",
            )),
        ]

        l1 = await _do_request(messages, temperature=0.2, frequency_penalty=0.1)
        assert l1

        fileref.summary = l1
        fp.write(f"```\n{fileref.summary}\n```\n\n")

        messages = [
            ChatMessage(role=ChatRole.USER, content=formatprompt(
                """
                Does this file summary reference any external services or APIs? If so, which ones? Exclude things like built-in libraries or API frameworks. For API client libraries, only include the name of the API, not the name of the library. For example:

                - Include "GitHub" but not "Octokit"
                - Include "Slack" but not "Slack SDK" or "Slack Bolt"

                Then, simplify and normalize the names of the APIs. For example:

                - "GitHub" instead of "GitHub API"
                - "OpenAI" instead of "OpenAI API"
                - "Confluence" instead of "Confluence Rest API"
                - "Google Cloud Secret Manager" instead of "Google Cloud's Secret Manager Service"

                Output your response as a JSON array of strings. If there are no references, return an empty JSON array. Your full response should be valid, parseable JSON.
                ===
                """,
                fileref.summary,
                """
                ===
                """,
            )),
        ]

        l1 = await _do_request(messages)
        assert l1

        fileref.service_references = [_normalize(s) for s in json.loads(l1)]
        fp.write(f"```json\n{json.dumps(fileref.service_references, indent=2)}\n```\n\n")
        fp.flush()

    for hdir in hierarchy.dirs:
        await gather_summaries(hierarchy=hdir, fp=fp)
        if hdir.service_name:
            pass

    summary_list = []

    for file in [x for x in hierarchy.files if x.summary]:
        summary_list.append(f"### File: {file.clean_path}\n\n{file.summary}")

    for hdir in [x for x in hierarchy.dirs if x.summary]:
        summary_list.append(f"### Directory: {hdir.clean_path}\n\n{hdir.summary}")

    if len(summary_list) > 0:
        dirsum = "\n\n".join(summary_list)

        messages = [
            ChatMessage(role=ChatRole.USER, content=formatprompt(
                f"""
                This is a list of names and summaries of the source code files in a directory{', and the names and summaries of its sub-directories' if len(hierarchy.dirs) > 0 else ''}. Decide if this directory contains a file that starts an application server. Then, if there is exactly one application server in this directory, create a short name (1-3 words) for the application. Otherwise, do not create a name.

                If you created a name for the application, respond with that name and nothing else. Otherwise, respond with the word "SENTINEL" and nothing else.

                ===
                """,
                dirsum,
                "===",
            )),
        ]

        l1 = await _do_request(messages, temperature=0, frequency_penalty=0)
        assert l1

        l1 = _normalize(l1)
        fp.write(f"## {hierarchy.clean_path}\n\n")
        fp.write("```\n")
        fp.write(f"{l1}\n")
        fp.write("```\n\n")

        if l1 != "sentinel":
            hierarchy.service_name = l1

    fp.flush()

def _normalize(string: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", string).lower()

if __name__ == "__main__":
    asyncio.run(run())
