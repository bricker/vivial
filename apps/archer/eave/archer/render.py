# MERMAID: https://mermaid.js.org/intro/n00b-syntaxReference.html
# https://mermaid.js.org/syntax/entityRelationshipDiagram.html
# https://mermaid.live/edit


import os
import re

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

def clean_fpath(path: str) -> str:
    return re.sub(os.environ["EAVE_HOME"], "", path)