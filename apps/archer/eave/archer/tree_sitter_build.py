import os
from tree_sitter import Language, Parser

_build_root = os.path.join(os.environ["EAVE_HOME"], ".build/tree-sitter")

Language.build_library(
    f"{_build_root}/languages.so",
    [
        f"{_build_root}/tree-sitter-typescript/typescript"
    ]
)