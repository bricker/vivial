import eave.stdlib.openai_client as _o
OPENAI_MODEL = _o.OpenAIModel.GPT4

DIR_EXCLUDES = set([
    r"node_modules",
    r"__pycache__",
    r"/vendor",
    r"/\.",
    r"/tests",
    r"eave_alembic",
])

FILE_INCLUDES = set([
    # r"worker/.+?\.py$",
    r"\.py",
    r"\.ts",
    # r"slack/brain/document_management\.py",
    # r"core/internal/orm/confluence_destination\.py",
    # r"slack/.+?\.py$"
    # r"core/.+?\.py$"
])