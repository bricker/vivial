import asyncio
from dataclasses import dataclass
import enum
import textwrap
from time import sleep
import uuid
from dotenv import load_dotenv
load_dotenv()

import re
import os
import eave.stdlib.openai_client as _o

import tiktoken

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-16k')

_excludes = set([
    r"node_modules",
    r"^__pycache__",
    r"^vendor",
    r"^\.",
    r"^tests",
    r"^eave_alembic",
])

_includes = set([
    # r"worker/.+?\.py$",
    r"\.py",
    r"\.ts",
    # r"slack/brain/document_management\.py",
    # r"core/internal/orm/confluence_destination\.py",
    # r"slack/.+?\.py$"
    # r"core/.+?\.py$"
])

# MERMAID: https://mermaid.js.org/intro/n00b-syntaxReference.html
# https://mermaid.js.org/syntax/entityRelationshipDiagram.html
# https://mermaid.live/edit

class Service:
    id: str
    name: str
    type_: str
    links: list["Service"]

    def __init__(self, name: str, type_: str) -> None:
        self.id = re.sub(" +", "", name)
        self.name = name
        self.type_ = type_
        self.links = []

class ServiceGraph(dict[str, Service]):

    def render(self) -> str:
        i = "    "
        lines: list[str] = []
        lines.append("graph TD")

        lines.append(f"{i}subgraph \"External\"")

        for x in [
            f"{s.id}({s.name})"
            for s in self.values()
            if s.type_ == "external"
        ]:
            lines.append(f"{i}{i}{x}")

        lines.append(f"{i}end")

        lines.append(f"{i}subgraph \"Internal\"")

        for x in [
            f"{s.id}({s.name})"
            for s in self.values()
            if s.type_ == "internal"
        ]:
            lines.append(f"{i}{i}{x}")

        lines.append(f"{i}end")

        for service in self.values():
            for link in service.links:
                lines.append(f"{i}{service.id}-->{link.id}")

        return "\n".join(lines)

async def run():
    # dirs = [
    #     ("slack", "Eave Slack App"),
    #     ("core", "Core API"),
    #     ("github", "Eave GitHub API"),
    #     ("confluence", "Eave Confluence API"),
    #     ("jira", "Eave Jira API"),
    # ]

    # dirs = [
    #     ("codalab", "Codalab"),
    # ]

    graph = ServiceGraph()

    for (dir, appname) in dirs:
        cservice = Service(name=appname, type_="internal")
        graph[appname] = cservice

        for root, dirs, files in os.walk(top=os.path.join(os.environ["EAVE_HOME"], "apps", dir)):
            dirs[:] = [d for d in dirs if all([not re.search(e, d) for e in _excludes])]

            for fname in [f for f in files if any([re.search(i, os.path.join(root, f)) for i in _includes])]:
                sleep(2)

                fpath = os.path.join(root, fname)
                [r, ext] = os.path.splitext(fname)
                lang = "python" if ext == "py" else "typescript"
                print(fpath)

                with open(fpath) as file:
                    contents = file.read()
                    contents = contents[:7500]

                if len(contents.strip()) == 0:
                    print("empty file, skipping")
                else:
                    prompt = _o.formatprompt(
                        """
                        The following {lang} code is part of an application that is part of a larger system.
                        Generate a short, human-readable name for the subsystem that this code is a part of. The name will be used in an architecture diagram for this repository.
                        Respond with only the short name and nothing else.
                        ###
                        {contents}
                        ###
                        """.format(lang=lang, contents=contents)
                    )

                    params = _o.ChatCompletionParameters(
                        messages=[
                            prompt
                        ],
                        model=_o.OpenAIModel.GPT_35_TURBO_16K,
                        temperature=0,
                        # frequency_penalty: Optional[float] = None
                        # presence_penalty: Optional[float] = None
                        # temperature: Optional[float] = None
                    )
                    responsea = await _o.chat_completion(params)
                    assert responsea
                    print(responsea)
                    svc = Service(name=responsea, type_="internal")
                    if not graph.get(svc.id):
                        graph[svc.id] = svc


                    prompt = _o.formatprompt(
                        """
                        The following {lang} code is part of an application that is part of a larger system. It is in a file called {fpath}.
                        Does this code depend on any external APIs, services, or systems? If so, list each one.
                        Omit standard library modules and other file imports. For example, logging, time, datetime, argparse, http.client should be omitted.
                        If there are no dependencies, respond with "none" and nothing else.
                        Format your response as a flat, unordered list, containing a short name for each API, service, or system.
                        After each item, add either exactly "External" or exactly "Internal" in parentheses indicating whether this is a third-party or first-party API, service, or system.
                        Do not group the services together. All items should be at the same level in the list.
                        Respond with only the list and nothing else.

                        ###
                        {contents}
                        ###
                        """.format(lang=lang, fpath=fpath, contents=contents)
                    )

                    params = _o.ChatCompletionParameters(
                        messages=[
                            prompt
                        ],
                        model=_o.OpenAIModel.GPT4,
                        temperature=0,
                        # frequency_penalty: Optional[float] = None
                        # presence_penalty: Optional[float] = None
                        # temperature: Optional[float] = None
                    )
                    responseb = await _o.chat_completion(params)
                    print(responseb)

                    if responseb and not re.match(r"^none$", responseb.lower()):
                        svclist = responseb.split("\n")
                        for service in svclist:
                            m = re.search(r"^- *(?P<name>.+?) *\((?P<type>.+?)\)$", service)
                            if m:
                                vars = m.groupdict()
                                svc2 = Service(name=vars["name"], type_=vars["type"].lower())
                                if not graph.get(svc2.id):
                                    graph[svc2.id] = svc2
                                svc.links.append(svc2)

                    print("\n\n")

    with open("graph.md", mode="w+") as f:
        r = graph.render()
        f.write(r)

    print("wrote output to graph.mermaid")

if __name__ == "__main__":
    asyncio.run(run())