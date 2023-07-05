
import os
import re

from eave.archer.config import DIR_EXCLUDES, FILE_INCLUDES


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
        if dirent.is_dir(follow_symlinks=False) and not any([re.search(e, path) for e in DIR_EXCLUDES]):
            child_hierarchy = build_hierarchy(root=path)
            hierarchy.dirs.append(child_hierarchy)
        elif dirent.is_file() and any([re.search(e, path) for e in FILE_INCLUDES]):
            hierarchy.files.append(path)

    return hierarchy