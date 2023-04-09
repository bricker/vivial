import enum
import re
from typing import List
import eave.stdlib.openai_client as eave_openai

async def get_topic(conversation: str) -> str:
    prompt = (
        "Create a short title for the following conversation. Respond with only the title and nothing else.\n\n"
        "The conversation is as follows:\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0.5,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response

async def get_hierarchy(conversation: str) -> List[str]:
    prompt = (
        "Create up to three cascading parent folder names for this conversation, from least specific to most specific. "
        "These folder names will be used to organize the conversation into a directory hierarchy for easier navigation. "
        "For example, the parent folders for a conversation about Python might be: Engineering, Python"
        "The parent folders for a conversation about a new project for the Marketing team might be: Marketing, Projects, [project name].\n"
        "Give the answer as a comma-separated list of category names from least specific to most specific.\n\n"
        "The conversation is as follows:\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0.9,
        presence_penalty=0.9,
        temperature=0,
    )

    answer: str | None = await eave_openai.chat_completion(openai_params)
    assert answer is not None

    parents = list(map(lambda x: x.strip(), reversed(answer.split(","))))
    return parents

async def get_project_title(conversation: str) -> str:
    prompt = (
        f"Is the following conversation about a specific project? If so, what is the name of the project? If not, say: {eave_openai.STOP_SEQUENCE}\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0.9,
        presence_penalty=0.9,
        temperature=0,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response

class DocumentationType(enum.Enum):
    TECHNICAL = "Technical Documentation"
    PROJECT = "Project One-Pager"
    TEAM_ONBOARDING = "Team Onboarding"
    ENGINEER_ONBOARDING = "Engineer Onboarding"
    UNKNOWN = "Other"

async def get_documentation_type(conversation: str) -> DocumentationType:
    prompt = (
        "You know how to write the following types of documentation:\n"
        f"- {DocumentationType.TECHNICAL.value}: This type of documentation is primarily used by engineers. It might describe how to setup a code repository, how to run tests, troubleshooting of local development environments, bug analysis, or other similar engineering tasks. It can also explain code, systems, architecture, and other engineering concerns.\n"
        f"- {DocumentationType.PROJECT.value}: This type of documentation is used by both product managers and engineers. It might contain information about a project such as an overview, product features, tasks, questions, planning, estimated timeline, stakeholders, team members, and requirements.\n"
        f"- {DocumentationType.TEAM_ONBOARDING.value}: This type of documentation is used by all new team members. It might contain information about the current team such as names, profile photos, and job titles. It can also list the team's preferred means of communication (for example, which Slack channels to use for different purposes), meeting schedule, and other information that the new team member needs to know to be successful on the team.\n"
        f"- {DocumentationType.ENGINEER_ONBOARDING.value}: This type of documentation is used by engineers who are new to the team. It might contain a list of code repositories that the engineer should clone and setup, a list of requisite or optional software to install and how to install it, a description of the team's git workflow. It may also explain how to procure equipment or software from the company, such as a new keyboard, a different monitor, or a specific IDE.\n"
        f"- {DocumentationType.UNKNOWN.value}: You can write any other type of documentation, but you prefer the types listed above when appropriate.\n\n"
        "Which of those types of documentation is most appropriate for the following conversation? Respond with just the type of documentation and nothing else.\n\n"
        "Conversation:\n\n"
        f"{conversation}\n\n"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None

    if re.search(DocumentationType.TECHNICAL.value, openai_response, flags=re.IGNORECASE):
        return DocumentationType.TECHNICAL
    elif re.search(DocumentationType.PROJECT.value, openai_response, flags=re.IGNORECASE):
        return DocumentationType.PROJECT
    elif re.search(DocumentationType.TEAM_ONBOARDING.value, openai_response, flags=re.IGNORECASE):
        return DocumentationType.TEAM_ONBOARDING
    elif re.search(DocumentationType.ENGINEER_ONBOARDING.value, openai_response, flags=re.IGNORECASE):
        return DocumentationType.ENGINEER_ONBOARDING
    else:
        return DocumentationType.UNKNOWN

async def get_documentation(conversation: str, documentation_type: DocumentationType) -> str:
    match documentation_type:
        case DocumentationType.TECHNICAL:
            setup = (
                f"Create Technical Documentation for the information in the following conversation. "
                "This documentation will be used primarily by software engineers."
            )
        case DocumentationType.PROJECT:
            setup = (
                f"Create a Project One-Pager document for the project being discussed in the following conversation. "
                "The document should be formatted as a table with the following headers: "
                "Category, Goal, Features, Notes\n"
                "Each row in the table should describe details of a feature in the project."
            )
        # case DocumentationType.TEAM_ONBOARDING:
        #     setup = (
        #         f"Create Team Onboarding documentation "
        #         "This documentation will be used primarily by software engineers."
        #     )
        #     pass
        # case DocumentationType.ENGINEER_ONBOARDING:
        #     setup = (
        #         f"Create Technical Documentation for the information in the following conversation. "
        #         "This documentation will be used primarily by software engineers."
        #     )
        #     pass
        case _:
            setup = (
                f"Create Documentation for the information in the following conversation."
            )
            pass

    prompt = (
        f"{setup}\n\n"
        "You should not simply summarize the conversation; "
        "instead, you should extract information that is important, novel, and is likely to be valuable to other team members in the future. "
        "The documentation should be formatted using plain HTML tags without any inline styling. "
        "The documentation will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>\n\n"
        f"The conversation is as follows:\n\n"
        f"{conversation}\n\n"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=3,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        temperature=0.5,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response
