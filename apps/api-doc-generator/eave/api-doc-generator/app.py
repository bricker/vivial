from typing import List
import asyncio
import os
import re
import subprocess
import eave.stdlib.openai_client as openai


# TODO: use Eave GitHub App to interact with GitHub.
def run(command: str) -> str:
    process = subprocess.run([command], shell=True, capture_output=True, text=True)
    if process.stderr:
        print(process.stderr)
    return process.stdout











# TODO: add YAML support.
async def document_express_apis(repo_name: str, repo_dir: str, wiki_dir: str) -> None:
    for root, dirs, files in os.walk(repo_dir):
        for name in files:
            if name == "package.json":
                requirements = open(f"{root}/{name}", mode="r").read()
                requires_express = re.search(r"[\"\']express[\"\']", requirements)
                if requires_express:

















# TODO: set up an API endpoint to run this logic (Idea: 1 endpoint per supported framework)
# TODO: this data should get pulled from elsewhere (likely the dash).
# TODO: ensure that wiki exists before attempting to create documentation.
# TODO: let Eave GitHub App handle interactions with GitHub.
async def main() -> None:

    repo_name = "eave-monorepo"
    repo = f"https://github.com/eave-fyi/{repo_name}.git"
    wiki = f"https://github.com/eave-fyi/{repo_name}.wiki.git"

    temp_dir = "temp"
    repo_dir = f"{temp_dir}/{repo_name}"
    wiki_dir = f"{temp_dir}/{repo_name}.wiki"

    # run(f"mkdir {temp_dir} && cd {temp_dir} && git clone {repo} && git clone {wiki}")

    await document_express_apis(repo_name, repo_dir, wiki_dir)

    run(f"cd {wiki_dir} && git add . && git commit -m 'Document APIs' && git push")
    # run(f"rm -rf {temp_dir}")

    print("✅ Successfully Documented APIs")


if __name__ == "__main__":
    asyncio.run(main())
