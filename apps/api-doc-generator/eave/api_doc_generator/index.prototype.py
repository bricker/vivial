from random import random, sample
from typing import List
import subprocess
import os
import asyncio
import eave.stdlib.openai_client as openai

# TODO: always display endpoint docs in the same order
# TODO: make prompt refinement
# TODO: use 4 spaces not 2
# TODO: drill down more layers when combining endpoint code
# TODO: strip out middleware
# TODO: clone in temp
# TODO: play around with leveraging an ast (e.g. use acorns for JS and ast for Python)
# TODO: total cleanup / refactor
# TODO: Scan the entry file one time, gathering all of the info you need.
# TODO: figure out how to effectively tell when functions are referenced.
# TODO: Research how to efficiently create an abstract syntax tree for each language.
# TODO: Test on many express API endpoints
# TODO: handle default exports
# TODO: handle require statements


def run(command: str) -> str:
  process = subprocess.run(
    [command],
    shell=True,
    capture_output=True,
    text=True
  )
  if process.stderr:
    print(process.stderr)
  return process.stdout


def extract_local_imports(dir_name: str, file_name: str) -> List[dict]:
  file = open(f"{dir_name}/{file_name}", mode="r")
  lines = file.readlines()
  imports = []

  for i in range(len(lines)):
    line = lines[i].strip()
    if line.startswith('import') or "= require(" in line:
      if line.endswith(";"):
        imports.append(line)
      else:
        condensed_import = line
        j = i + 1
        while ";" not in lines[j]:
          condensed_import += lines[j].strip()
          j += 1
        condensed_import += lines[j].strip()
        imports.append(condensed_import)

  import_locations = []
  for line in imports:
    location = line.split(" ")[-1]
    location = location[1:len(location) - 2]

    # TODO: handle edge case where location starts with "../"
    if location[0] == ".":
      location = dir_name + location[1:]

      if location.endswith(".js") or location.endswith(".ts"):
        i = line.find("{")
        if i == -1:
          item = line.split(" ")[1]
          import_locations.append((location, item))
        else:
          j = line.find("}", i)
          items = line[i + 1:j]
          import_locations.append((location, items.strip()))

  result = {}
  for location in import_locations:

    import_list = location[1].split(",")
    for i in range(len(import_list)):
      import_list[i] = import_list[i].strip()

    file_path = location[0]
    file = None

    # TODO: figure out more elegant way to handle .js used in .ts apps.
    try:
      file = open(file_path, mode="r")
    except FileNotFoundError:
      file_path = file_path.split(".js")[0] + ".ts"
      file = open(file_path, mode="r")

    if file is not None:
      lines = file.readlines()
      for i in range(len(lines)):
        line = lines[i]
        for item in import_list:
          if item in line:
            code = line
            j = i + 1

            # TODO: figure out more reliable way to determine end of import code.
            while lines[j].rstrip() not in ["}", "};", "});"]:
              code += lines[j]
              j += 1
            code += lines[j]
            result[item] = code

  return result


# TODO: Determine best way to guess API name.
def extract_express_api_name(dir_name: str) -> str:
  cleaned_dir_name = dir_name.replace("-", " ").replace("_", " ")
  return f"{cleaned_dir_name.title()} API Documentation"


# TODO: optimize extraction process.
def extract_express_api_endpoints(dir: str) -> List[str]:
  api_entry_dir = None
  api_entry_name  = None
  api_app_var = None
  api_router_var = None

  for root, dirs, files in os.walk(dir):

    # TODO: Determine if we want to make this assumption about test directories.
    # TODO: Determine what other folders can be ignored
    if root in ["test", ".git", "node_modules"]:
      continue

    for name in files:
      if name.endswith(".ts") or name.endswith(".js"):
        file = open(f"{root}/{name}", mode="r")
        for line in file.readlines():

          # TODO: Determine best way to detect entry Express API entry file.
          if "= express(" in line:
            api_entry_dir = root
            api_entry_name = name

            # TODO: figure out better way to isolate app variable.
            api_app_var = line.split(" ")[-3].strip()
            break

  if api_entry_name is None:
    return []

  api_entry_imports = extract_local_imports(api_entry_dir, api_entry_name)
  api_file = open(f"{api_entry_dir}/{api_entry_name}", mode="r")
  api_file_lines = api_file.readlines()

  # TODO:figure out better way to determine if router is used.
  for line in api_file_lines:
    if ("= Router(" in line) or ("= express.Router(" in line):
      api_router_var = line.split(" ")[-3].strip()
      break

  base_code = ""
  for i in range(len(api_file_lines)):
    line = api_file_lines[i]
    app_eq = api_app_var + " ="
    router_eq = api_router_var
    if api_router_var is not None:
      router_eq += " ="
    app_use = api_app_var + ".use("

    if app_eq in line or (api_router_var is not None and router_eq in line) or app_use in line:
      if line.rstrip().endswith(";"):
        base_code += line
      else:
        callback = line
        i += 1
        line = api_file_lines[i]
        while True:
          if line.rstrip() == "});" or line.rstrip() == "}));":
            break

          for key in api_entry_imports:
            if key in line:
              base_code += api_entry_imports[key]
          callback += line
          i += 1
          line = api_file_lines[i]

        callback += line
        base_code += callback

  api_endpoints = []
  for i in range(len(api_file_lines)):
    line = api_file_lines[i]
    endpoint = None

    router_use = api_router_var
    if router_use is not None:
      router_use = api_router_var + ".use("
    app_get = api_app_var + ".get("
    app_post = api_app_var + ".post("
    app_put = api_app_var + ".put("
    app_delete = api_app_var + ".delete("

    if (api_router_var is not None and router_use in line) or app_get in line or app_post in line or app_put in line or app_delete in line:
      endpoint = base_code

      if line.rstrip().endswith(");"):
        for key in api_entry_imports:
          if key in line:
            endpoint += api_entry_imports[key]
        endpoint += line
      else:
        callback = line
        i += 1
        line = api_file_lines[i]
        while line.rstrip() != "});":
          for key in api_entry_imports:
            if key in line:
              endpoint += api_entry_imports[key]
          callback += line
          i += 1
          line = api_file_lines[i]

        callback += line
        endpoint += callback

    if endpoint is not None:
      api_endpoints.append(endpoint)

  return api_endpoints


async def generate_express_api_docs(api_endpoints: List[str]) -> str:
  api_docs = ""

  for api_endpoint in api_endpoints:
  # for api_endpoint in sample(api_endpoints, 3):
    print("About to document endpoint...")

    openai_params = openai.ChatCompletionParameters(
      messages=[
        openai.ChatMessage(role=openai.ChatRole.SYSTEM, content=openai.formatprompt(
          """
          You will be given a block of javascript code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

          Your task is to generate API documentation for the provided Express REST API endpoint.

          Use the following template to format your response:

          ## {description of the API endpoint in at most 4 words}

          ```
          {HTTP Method} {Path}
          ```

          {high-level description of what the API endpoint does}

          ### Path Parameters

          **{name}** ({type}) *{optional or required}* - {description}

          ### Example Request

          ```
          {example request}
          ```

          ### Example Response

          ```
          {example response}
          ```

          ### Response Codes

          **{response code}**: {explanation of when this response code will be returned}

          <br />

          """
        )),
        openai.ChatMessage(role=openai.ChatRole.USER, content=openai.formatprompt(
          f"""
          !!!
          {api_endpoint}
          """
        )),
      ],
      model=openai.OpenAIModel.GPT4
    )
    response = await openai.chat_completion(params=openai_params)
    if response is not None:
      api_docs += response
      api_docs += "\n\n"

    print("Finished documenting endpoint...")

  return api_docs

async def document_express_apis(repo_name: str) -> None:
  for root, dirs, files in os.walk(repo_name):
    for name in files:

      # TODO: Add YAML support.
      if name == "package.json":
        package_content = open(f"{root}/{name}", mode='r').read()
        uses_express = package_content.find("express") != -1

        # TODO: Determine best way to detect that an app is an Express app.
        if (uses_express):
          api_endpoints = extract_express_api_endpoints(root)
          if api_endpoints:
            api_name = extract_express_api_name(root.split("/")[-1])
            api_docs = await generate_express_api_docs(api_endpoints)

            file_name = api_name + ".md"
            file_path = f"{repo_name}.wiki/" + file_name

            if os.path.exists(file_path):
              os.remove(file_path)

            f = open(file_path, "x")
            f.write(api_docs)
            f.close()
        break


async def main():
  # TODO: Fetch this info from dash (?)
  # repo = "https://github.com/eave-fyi/eave-monorepo.git"
  # wiki = "https://github.com/eave-fyi/eave-monorepo.wiki.git"
  # repo_name = "eave-monorepo"

  repo = "https://github.com/eave-fyi/test-photo-share-app.git"
  wiki = "https://github.com/eave-fyi/test-photo-share-app.wiki.git"
  repo_name = "test-photo-share-app"

  run(f"git clone {repo}")
  run(f"git clone {wiki}")

  await document_express_apis(repo_name)

  run(f"cd {repo_name}.wiki && git add . && git commit -m 'Update API Docs.' && git push")
  run(f"rm -rf {repo_name}")
  run(f"rm -rf {repo_name}.wiki")

if __name__ == "__main__":
  asyncio.run(main())
