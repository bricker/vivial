
from dataclasses import dataclass
import os
import re
from typing import Optional, Tuple

from eave.archer.config import EXCLUDES, PROJECT_ROOT
from eave.archer.util import clean_fpath, get_file_contents

class FileReference:
    path: str
    basename: str
    ext: str
    summary: Optional[str] = None
    external_service_references: list[str]
    internal_service_references: list[str]

    def __init__(self, path: str) -> None:
        self.path = path
        self.basename = os.path.basename(path)
        self.ext = os.path.splitext(self.basename)[1]
        self.external_service_references = []
        self.internal_service_references = []

    def read_file(self) -> str | None:
        c = get_file_contents(self.path)
        return c

    @property
    def clean_path(self) -> str:
        return clean_fpath(self.path, PROJECT_ROOT)

class FSHierarchy:
    root: str
    dirs: list["FSHierarchy"]
    files: list[FileReference]
    summary: Optional[str] = None
    service_name: Optional[str] = None

    def __init__(self, root: str) -> None:
        self.root = root
        self.dirs = []
        self.files = []

    @property
    def clean_path(self) -> str:
        return clean_fpath(self.root, PROJECT_ROOT)

def build_hierarchy(root: str) -> FSHierarchy:
    hierarchy = FSHierarchy(root=root)

    for dirent in os.scandir(path=root):
        path = os.path.join(root, dirent.name)
        if not any([re.search(e, path) for e in EXCLUDES]):
            if dirent.is_dir(follow_symlinks=False):
                child_hierarchy = build_hierarchy(root=path)
                hierarchy.dirs.append(child_hierarchy)
            elif dirent.is_file():
                hierarchy.files.append(FileReference(path=path))

    return hierarchy