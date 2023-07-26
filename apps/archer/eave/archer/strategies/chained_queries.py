from asyncio import sleep
import json

from eave.archer.config import OUTDIR, PROJECT_ROOT
from eave.archer.fs_hierarchy import FSHierarchy
from eave.stdlib.logging import eaveLogger
import eave.stdlib.openai_client as _o
from eave.archer.util import clean_fpath, get_file_contents, make_openai_request, truncate_file_contents_for_model


async def query_file_contents_chained(hierarchy: FSHierarchy, model: _o.OpenAIModel) -> None:
    await query_file_contents(filepath=f"{PROJECT_ROOT}/apps/core/eave/core/public/requests/oauth/google_oauth.py", model=model)

    # for file in hierarchy.files:
    #     await query_file_contents(filepath=file, model=model)

    # for dirh in hierarchy.dirs:
    #     await query_file_contents_chained(hierarchy=dirh, model=model)

async def query_file_contents(filepath: str, model: _o.OpenAIModel) -> None:
    async def _do_request(messages: list[_o.ChatMessage]) -> str | None:
        params = _o.ChatCompletionParameters(
            messages=messages,
            model=model,
            temperature=2,
            presence_penalty=0,
            frequency_penalty=-2,
        )

        response = await make_openai_request(filepath=filepath, params=params)
        if not response:
            return None

        answer = _o.get_choice_content(response)
        if not answer:
            return None

        eaveLogger.info(f"{filepath}\n{answer}\n")

        with open(f"{OUTDIR}/files.md", "a") as f:
            f.write(f"```\n{answer}\n```\n")

        return answer



    if model == _o.OpenAIModel.GPT4:
        await sleep(2)

    with open(f"{OUTDIR}/files.md", "a") as f:
        f.write(f"### {clean_fpath(filepath, prefix=PROJECT_ROOT)}\n\n")

    file_contents = get_file_contents(filepath, model=model)
    if not file_contents:
        return None

    code = truncate_file_contents_for_model(file_contents=file_contents, prompt="", model=model)

    messages = [
        _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
            f"""
            List the external services referenced in this code.

            !!!
            {code}
            !!!
            """
        )),
    ]

    answer = await _do_request(messages)
    if not answer:
        return None
    alist = json.loads(answer)
    if len(alist) == 0:
        return None

    # flist = [f"- {e}\n" for e in alist]

    # messages = [
    #     _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
    #         f"""
    #         This is a list of external services referenced from an application:

    #         !!!
    #         {flist}
    #         !!!

    #         Are there any references to Google Cloud, AWS, or Azure products? If so, which products are these references a part of?
    #         """
    #     )),
    # ]

    # answer = await _do_request(messages)
