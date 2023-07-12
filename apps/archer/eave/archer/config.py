import os
import eave.stdlib.openai_client as _o

PROJECT_ROOT = os.environ["EAVE_HOME"]

# TODO: Automatically exclude files in gitignore

# Files and directories that are excluded from hierarchy
EXCLUDES = set([
    r"node_modules",
    r"__pycache__",
    r"/vendor/",
    r"/vendor$",
    r"/\.",
    r"/build/",
    r"/build$",
    r"/dist/",
    r"/dist$",
    r"\.egg-info",
    r"/tests/",
    r"/tests$",
    r"/bin/",
    r"/bin$",
])

# Files that are excluded from dependency collection, but still show in the hierarchy.
# The entries in EXCLUDES are implicity included here, because dependency collection only checks files in the produced hierarchy.
CONTENT_EXCLUDES = set([
    r"\.ya?ml",
    r"\.(png|jpg|jpeg|svg)",
    r"package-lock\.json",
])

