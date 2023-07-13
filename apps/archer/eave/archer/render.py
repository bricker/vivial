# MERMAID: https://mermaid.js.org/intro/n00b-syntaxReference.html
# https://mermaid.js.org/syntax/entityRelationshipDiagram.html
# https://mermaid.live/edit


from datetime import datetime
import json
from math import trunc
import os
import sys
from textwrap import dedent

from .service_registry import REGISTRY
from .config import PROJECT_ROOT
import eave.stdlib.openai_client as _o

from eave.archer.util import PROMPT_STORE, TOTAL_TOKENS, clean_fpath, get_tokens

from eave.archer.fs_hierarchy import FSHierarchy

from eave.archer.service_graph import Service, ServiceGraph

_TAB = "    "
_STAB = "  "
_ARROW = "-->"

def _gather_services(graph: ServiceGraph, deps: dict[str, Service]) -> None:
    for service in graph.services.values():
        if service.id not in deps:
            deps[service.id] = service
            _gather_services(graph=service.subgraph, deps=deps)

def _render_subgraph(service: Service, ilevel: int) -> str:
    lines = list[str]()

    for dep in service.subgraph.services.values():
        if not dep.visited:
            dep.visited = True
            lines.append(_render_subgraph(dep, ilevel))

        lines.append(f"{_TAB * ilevel}{service.id}{_ARROW}{dep.id}")

    out = "\n".join(lines)
    return out

    # lines.append(f"{i}subgraph \"External\"")

    # for x in [
    #     f"{s.id}({s.name})"
    #     for s in self.services.values()
    #     if s.type_ == "external"
    # ]:
    #     lines.append(f"{i}{i}{x}")

    # lines.append(f"{i}end")

    # lines.append(f"{i}subgraph \"Internal\"")

    # for x in [
    #     f"{s.id}({s.name})"
    #     for s in self.services.values()
    #     if s.type_ == "internal"
    # ]:
    #     lines.append(f"{i}{i}{x}")

    # lines.append(f"{i}end")

    # for service in self.services.values():

    #     for  in service.links:
    #         lines.append(f"{i}{service.id}-->{link.id}")

    # return "\n".join(lines)

def render_root_graph(graph: ServiceGraph) -> str:
    lines = list[str]()
    i = _TAB

    lines.append("graph LR")

    deps = dict[str, Service]()
    _gather_services(graph=graph, deps=deps)
    for service in deps.values():
        lines.append(f"{i}{service.definition}")

    for service in graph.services.values():
        lines.append(_render_subgraph(service, 1))

    out = "\n".join(lines)
    return out

def render_fs_hierarchy(hierarchy: FSHierarchy, parent: FSHierarchy | None = None, ilevel: int = 0) -> str:
    lines = list[str]()

    fname = clean_fpath(hierarchy.root, prefix=parent.root if parent else PROJECT_ROOT) or "(root)"
    lines.append(f"{_STAB * ilevel}- {fname}")

    for dirh in hierarchy.dirs:
        lines.append(render_fs_hierarchy(hierarchy=dirh, parent=hierarchy, ilevel=ilevel + 1))

    for filename in hierarchy.files:
        fname = clean_fpath(filename, prefix=hierarchy.root)
        lines.append(f"{_STAB * (ilevel + 1)}- {fname}")

    out = "\n".join(lines)
    return out

_ts_format = "%Y-%m-%d--%H:%M:%S"

def write_services(timestamp: datetime) -> None:
    pdir = _pdir(timestamp)
    filename = f"{pdir}/services.md"
    key = "get_services"
    values = PROMPT_STORE.get(key)
    if not values:
        return

    with open(filename, mode="a") as file:
        file.write("### Services\n\n")
        for service in REGISTRY.services.values():
            file.write(f"- **{service.name}** ({service.id}): {service.description}\n")
            for service in service.subgraph.services.values():
                file.write(f"  - {service.name}\n")
        file.write("\n\n")

    write_prompt(filename=filename, key=key)
    write_openai_request(filename=filename, key=key)

def write_dependencies(timestamp: datetime) -> None:
    pdir = _pdir(timestamp)
    filename = f"{pdir}/dependencies.md"
    key = "get_dependencies"
    values = PROMPT_STORE.get(key)
    if not values:
        return

    write_prompt(filename=filename, key=key)
    write_openai_request(filename=filename, key=key)

def write_prompt(filename: str, key: str) -> None:
    values = PROMPT_STORE.get(key)
    if not values:
        return

    with open(filename, mode="a") as file:
        file.write("### Prompt\n\n")
        for message in values[0].messages:
            file.write("```\n")
            file.write(f"{message.role.upper()}:\n{message.content}\n")
            file.write("```\n\n")

def write_openai_request(filename: str, key: str) -> None:
    values = PROMPT_STORE.get(key)
    if not values:
        return None

    with open(filename, mode="a") as file:
        file.write("### Request\n\n")
        file.write("```json\n")
        file.write(json.dumps(values[0].compile(), indent=2))
        file.write("\n```\n\n")

        file.write("### Response\n\n")
        file.write("```json\n")
        file.write(json.dumps(values[1], indent=2))
        file.write("\n```\n\n")

def write_hierarchy(timestamp: datetime, hierarchy: FSHierarchy, model: _o.OpenAIModel) -> None:
    pdir = _pdir(timestamp)
    rendered_hierarchy = render_fs_hierarchy(hierarchy=hierarchy).strip()
    tokenlen = len(get_tokens(rendered_hierarchy, model))

    with open(f"{pdir}/hierarchy.md", mode="a") as file:
        file.write(f"Tokens: {tokenlen}\n\n")
        file.write("```\n")
        file.write(rendered_hierarchy)
        file.write("\n```\n\n")


def write_graph(timestamp: datetime, rendered_graph: str) -> None:
    pdir = _pdir(timestamp)

    with open(f"{pdir}/graph.md", mode="a") as file:
        file.write("```mermaid\n")
        file.write(rendered_graph.strip())
        file.write("\n```\n\n")

def write_run_info(timestamp: datetime) -> None:
    delta = datetime.now() - timestamp
    duration = trunc(delta.total_seconds())
    pdir = _pdir(timestamp)

    # https://openai.com/pricing
    # GPT4 8k: prompt=$0.03/1K tokens, completion=$0.06/1K tokens
    cost = round(
        (
            ((TOTAL_TOKENS['prompt'] / 10e3) * 0.03) +
            ((TOTAL_TOKENS['completion'] / 10e3) * 0.06)
        ), 2
    )

    with open(f"{pdir}/run_info.md", mode="a") as file:
        file.write(f"- Prompt tokens: {TOTAL_TOKENS['prompt']}\n")
        file.write(f"- Completion tokens: {TOTAL_TOKENS['completion']}\n")
        file.write(f"- Total tokens: {TOTAL_TOKENS['total']}\n")
        file.write(f"- Cost: ${cost}\n")
        file.write(f"- Duration: {duration}\n")

    print("duration=", duration, "tokens=", TOTAL_TOKENS["total"], "cost=", f"${cost}")

def _pdir(timestamp: datetime) -> str:
    dateformat = timestamp.strftime(_ts_format)
    pdir = f".out/{dateformat}"
    os.makedirs(pdir, exist_ok=True)
    return pdir

"""
Example Mermaid C4 Content diagram
https://mermaid.js.org/syntax/c4c.html
https://github.com/plantuml-stdlib/C4-PlantUML/blob/master/README.md#system-context-system-landscape-diagrams

As of July 2023, C4 diagrams in Mermaid are experimental and not viable for this use-case, mostly because of the relationship lines overlapping other shapes.

C4Context
    title Eave System Architecture
    System_Boundary(BoundaryGCP, "Google Cloud") {
        System(SystemCoreAPI, "Eave Core API", "description")
        System(SystemSlackApp, "Eave Slack App", "description")
        System(SystemGithubApp, "Eave Github App", "description")
        System(SystemJiraApp, "Eave Jira App", "description")
        System(SystemConfluenceApp, "Eave Confluence App", "description")
        System(SystemWWW, "Eave Website", "description")
    }

    System_Boundary(BoundaryExternal, "Third-Party") {
        System(SystemSlack, "Slack API", "description")
        System(SystemGithub, "Github API", "description")
        System(SystemAtlassian, "Atlassian APIs", "description")
    }


    BiRel(SystemWWW, SystemCoreAPI, "Reads and writes data")
    BiRel(SystemSlackApp, SystemCoreAPI, "Reads and writes data")
    BiRel(SystemGithubApp, SystemCoreAPI, "Reads and writes data")
    BiRel(SystemJiraApp, SystemCoreAPI, "Reads and writes data")
    BiRel(SystemConfluenceApp, SystemCoreAPI, "Reads and writes data")
    BiRel(SystemSlackApp, SystemGithubApp, "Reads and writes data")

    BiRel(SystemCoreAPI, SystemSlack, "Reads and writes data")
    BiRel(SystemSlackApp, SystemSlack, "Reads and writes data")

    BiRel(SystemConfluenceApp, SystemAtlassian, "Reads and writes data")
    BiRel(SystemJiraApp, SystemAtlassian, "Reads and writes data")
"""