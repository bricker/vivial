from datetime import datetime
import os
import eave.stdlib.openai_client as _o

PROJECT_ROOT = os.environ["EAVE_HOME"]

TIMESTAMP = datetime.now()
TIMESTAMPF = TIMESTAMP.strftime("%Y-%m-%d--%H:%M:%S")
OUTDIR = f".out/{TIMESTAMPF}"
os.makedirs(OUTDIR, exist_ok=True)

# TODO: Automatically exclude files in gitignore
# https://pypi.org/project/pathspec/

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
    r"/terraform",
    r"\.bash",
    r"requirements.*\.txt",
    r"\.md",
    r"alembic",
    r"\.ya?ml",
    r"\.(png|jpg|jpeg|svg)",
    r"package-lock\.json",
    r"\.crt",
    r"\.key",
    r"\.pem",
    r"\.env",
    r"tsconfig\.json",
    r"\.eslintrc",
])

# Files that are excluded from dependency collection, but still show in the hierarchy.
# The entries in EXCLUDES are implicity included here, because dependency collection only checks files in the produced hierarchy.
CONTENT_EXCLUDES: set[str] = set()

