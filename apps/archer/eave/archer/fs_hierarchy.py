
import os
import re

from eave.archer.config import EXCLUDES


class FSHierarchy:
    root: str
    dirs: list["FSHierarchy"]
    files: list[str]

    def __init__(self, root: str) -> None:
        self.root = root
        self.dirs = []
        self.files = []

def build_hierarchy(root: str) -> FSHierarchy:
    hierarchy = FSHierarchy(root=root)

    for dirent in os.scandir(path=root):
        path = os.path.join(root, dirent.name)
        if not any([re.search(e, path) for e in EXCLUDES]):
            if dirent.is_dir(follow_symlinks=False):
                child_hierarchy = build_hierarchy(root=path)
                hierarchy.dirs.append(child_hierarchy)
            elif dirent.is_file():
                hierarchy.files.append(path)

    return hierarchy