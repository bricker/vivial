# MERMAID: https://mermaid.js.org/intro/n00b-syntaxReference.html
# https://mermaid.js.org/syntax/entityRelationshipDiagram.html
# https://mermaid.live/edit


from datetime import datetime
import os
import re
import eave.stdlib.openai_client as _o
from .config import OPENAI_MODEL

from .util import clean_fpath

from .fs_hierarchy import FSHierarchy

from .service_graph import Service, ServiceGraph

_TAB = "    "
_ARROW = "-->"

def _gather_services(graph: ServiceGraph, deps: dict[str, Service]) -> None:
    for service in graph.services.values():
        deps.setdefault(service.id, service)
        _gather_services(graph=service.subgraph, deps=deps)

def _render_subgraph(service: Service, ilevel: int) -> str:
    lines = list[str]()

    for dep in service.subgraph.services.values():
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

def render_fs_hierarchy(hierarchy: FSHierarchy, ilevel: int = 0) -> str:
    lines = list[str]()

    fname = clean_fpath(hierarchy.root)
    lines.append(f"{_TAB * ilevel}- {fname}")

    for dirh in hierarchy.dirs:
        lines.append(render_fs_hierarchy(dirh, ilevel + 1))

    for filename in hierarchy.files:
        fname = clean_fpath(filename)
        lines.append(f"{_TAB * (ilevel + 1)}- {fname}")

    out = "\n".join(lines)
    return out

def fileout(fname: str, timestamp: datetime, messages: list[str|_o.ChatMessage], rendered_graph: str) -> None:
    dateformat = timestamp.strftime("%Y-%m-%d--%H:%M:%S")
    pdir = f".out/{dateformat}"
    os.makedirs(pdir)

    outfile=f"{pdir}/{timestamp}/{fname}"
    with open(outfile, mode="a") as f:
        f.write(f"Timestamp: {dateformat}\n\n")
        f.write(f"Model: {OPENAI_MODEL}")

        f.write("\n\n### Prompt:\n")
        f.write("```")

        for message in messages:
            role = message.role if isinstance(message, _o.ChatMessage) else _o.ChatRole.USER
            text = message.content if isinstance(message, _o.ChatMessage) else message
            f.write(f"{role}: {text}\n\n")

        f.write("```\n\n")

        f.write("### Result\n")
        f.write("```mermaid\n")
        f.write(rendered_graph)
        f.write("\n```")
