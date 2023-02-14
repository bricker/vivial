from typing import Any


class ConfluencePageLinks:
    editui: str
    webui: str
    context: str
    self_: str
    tinyui: str
    collection: str
    base: str

    def __init__(self, data: dict[str, str]) -> None:
        self.base = data["base"]
        self.editui = data["editui"]
        self.webui = data["webui"]
        self.context = data["context"]
        self.self_ = data["self"]
        self.tinyui = data["tinyui"]
        self.collection = data["collection"]

    @property
    def editui_url(self) -> str:
        return self.base + self.editui

    @property
    def webui_url(self) -> str:
        return self.base + self.webui

    @property
    def tinyui_url(self) -> str:
        return self.base + self.tinyui


class ConfluencePage:
    links: ConfluencePageLinks
    id: str
    type: str
    status: str
    title: str
    space: dict[str, Any]
    history: dict[str, Any]
    version: dict[str, Any]
    ancestors: list[dict[str, Any]]
    container: dict[str, Any]
    macro_rendered_output: dict[str, Any]
    body: dict[str, Any]
    extensions: dict[str, Any]
    expandable: dict[str, Any]

    def __init__(self, data: dict[str, Any]) -> None:
        links: dict[str, str] = data["_links"]
        self.links = ConfluencePageLinks(data=links)
        self.id = data["id"]
        self.type = data["type"]
        self.status = data["status"]
        self.title = data["title"]
        self.space = data["space"]
        self.history = data["history"]
        self.version = data["version"]
        self.ancestors = data["ancestors"]
        self.container = data["container"]
        self.macro_rendered_output = data["macroRenderedOutput"]
        self.body = data["body"]
        self.extensions = data["extensions"]
        self.expandable = data["_expandable"]
