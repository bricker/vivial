import sys

from eave.dev_tooling.dotenv_loader import load_dotenv

sys.path.append(".")

load_dotenv("develop/shared/share.env", override=True)
load_dotenv(".env", override=True)

from eave.demo.app import app  # noqa: E402

if __name__ == "__main__":
    app.run(
        port=5000,
        use_debugger=False,
        use_reloader=True,
        extra_files=[
        ],
        exclude_patterns=[
            ".*",
            "**/build/",
            "**/__pycache__",
            "*.egg-info",
            "**/node_modules",
        ],
    )
