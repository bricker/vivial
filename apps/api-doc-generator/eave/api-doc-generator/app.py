from typing import List
import asyncio
import os
import re
from urllib import response
from xmlrpc.client import boolean
import pydantic
import requests
import subprocess
from eave.stdlib.requests import make_request
from eave.stdlib.eave_origins import EaveOrigin
import eave.stdlib.openai_client as openai

# TODO: remove.
import pprint
pp = pprint.PrettyPrinter(indent=0)


DIRS_TO_IGNORE = [
    "test",
    "tests",
    "node_modules",
    "bin",
]


# TODO: use proper eave request lib.
def get_ast(typescript: str) -> dict:
    EAVE_AST_TS_API_URL = "http://apps.eave.run:8080/ast-ts/api"
    EAVE_HEADERS = {
        'X-Google-EAVEDEV': "posix.uname_result(sysname='Darwin', nodename='Leilenahs-MacBook-Air.local', release='21.6.0', version='Darwin Kernel Version 21.6.0: Thu Jun  8 23:57:12 PDT 2023; root:xnu-8020.240.18.701.6~1/RELEASE_X86_64', machine='x86_64')",
        'eave-signature': 'dev',
        'eave-team-id': '21a89307-a8da-459f-b242-db75c28690be',
        'eave-origin': 'eave_api'
    }
    body = {
        'typescript': typescript
    }
    response = requests.post(
        url=f"{EAVE_AST_TS_API_URL}/parse",
        headers=EAVE_HEADERS,
        json=body
    )
    return response.json()


# TODO: use Eave GitHub App to interact with GitHub.
def run(command: str) -> str:
    process = subprocess.run([command], shell=True, capture_output=True, text=True)
    if process.stderr:
        print(process.stderr)
    return process.stdout


def extract_express_api_name(api_dir: str) -> str:
    return ""




def extract_express_api_endpoints(api_path: str) -> List[str]:
    for root, dirs, files in os.walk(api_path):
        dir = root.split("/")[-1]
        if dir in DIRS_TO_IGNORE:
            continue

        for name in files:
            is_target_file = name.endswith(".ts") or name.endswith(".js")
            if is_target_file:
                code = open(f"{root}/{name}", mode="r").read()
                ast = get_ast(code)
                print("*" * 50)
                print(code)
                print("-" * 50)
                pp.pprint(ast)








    return []










async def generate_express_api_doc(api_endpoints: List[str]) -> str:
    return ""


# TODO: figure out if you can pull all GitHub files of a specific type.
# TODO: add YAML support.
async def document_express_apis(repo_path: str, wiki_path: str) -> None:
    for root, dirs, files in os.walk(repo_path):
        for name in files:
            if name == "package.json":
                requirements = open(f"{root}/{name}", mode="r").read()
                requires_express = re.search(r"[\"\']express[\"\']", requirements)
                if requires_express:
                    api_endpoints = extract_express_api_endpoints(root)
                    if api_endpoints:
                        api_doc = await generate_express_api_doc(api_endpoints)
                break


# TODO: set up an API endpoint to run this logic (Idea: 1 endpoint per supported framework)
# TODO: this data should get pulled from elsewhere (likely the dash).
# TODO: ensure that wiki exists before attempting to create documentation.
# TODO: let Eave GitHub App handle interactions with GitHub.
async def main() -> None:

    repo_name = "eave-monorepo"
    repo = f"https://github.com/eave-fyi/{repo_name}.git"
    wiki = f"https://github.com/eave-fyi/{repo_name}.wiki.git"

    temp_dir = "temp"
    repo_path = f"{temp_dir}/{repo_name}"
    wiki_path = f"{temp_dir}/{repo_name}.wiki"

    # run(f"mkdir {temp_dir} && cd {temp_dir} && git clone {repo} && git clone {wiki}")

    await document_express_apis(repo_path, wiki_path)

    run(f"cd {wiki_path} && git add . && git commit -m 'Document APIs' && git push")
    # run(f"rm -rf {temp_dir}")

    print("✅ Successfully Documented APIs")


if __name__ == "__main__":
    asyncio.run(main())
