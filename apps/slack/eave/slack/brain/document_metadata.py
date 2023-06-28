import enum
import re
from typing import Optional
from eave.stdlib.exceptions import OpenAIDataError
from .message_prompts import CONVO_STRUCTURE
import eave.stdlib.openai_client as eave_openai

STRIPPED_CHARS = "\"' "


async def get_topic(conversation: str) -> str:
    prompt = eave_openai.formatprompt(
        f"""
        Create a short title for the following conversation. Respond with only the title and nothing else.

        {CONVO_STRUCTURE}

        Conversation:
        ###
        {conversation}
        ###
        """
    )

    openai_params = eave_openai.ChatCompletionParameters(
        model=eave_openai.OpenAIModel.GPT_35_TURBO_16K,
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0.5,
    )

    title: str | None = await eave_openai.chat_completion(openai_params)
    if title is None:
        raise OpenAIDataError()

    # Remove quotes and spaces at the beginning or end
    title = title.strip(STRIPPED_CHARS)
    return title


async def get_hierarchy(conversation: str) -> list[str]:
    # prompt = eave_openai.formatprompt(
    #     f"""
    #     Create up to two cascading parent folder names for this conversation, from least specific to most specific. These folder names will be used to organize the conversation into a directory hierarchy for easier navigation.

    #     Examples:
    #     - The parent folders for a conversation about Python might be: Engineering, Python.
    #     - The parent folders for a conversation about a new project for the Marketing team might be: Marketing, Projects

    #     Give the answer as a comma-separated list of category names, sorted from least specific to most specific.

    #     {CONVO_STRUCTURE}

    #     Conversation:
    #     ###
    #     {conversation}
    #     ###
    #     """
    # )
    prompt = eave_openai.formatprompt(
        f"""
        Create a parent folder name for this conversation. This folder names will be used to organize the conversation into a directory hierarchy for easier navigation.

        Examples of potential parent folder names for a conversation topic:
        - Conversation Topic: Python programming; Possible Parent Folder: "Engineering"
        - Conversation Topic: bugs or features for a beta version of a product; Possible Parent Folder: "Beta".
        - Conversation Topic: new product features; Possible Parent Folder: "Product Development" or "Product One-Pagers".
        - Conversation Topic: growth KPIs for a product; Possible Parent Folder: "Analytics" or "Growth".
        - Conversation Topic: go to market strategy; Possible Parent Folder: "Business" or "Go to Market".
        - Conversation Topic: designs for the marketing website; Possible Parent Folder: "Design" or "Marketing Website".
        - Conversation Topic: onboarding experience for new users; Possible Parent Folder: "Product Development" or "Onboarding".
        - Conversation Topic: onboarding team members; Possible Parent Folder: "Employee Resources" or "Team Onboarding".
        - Conversation Topic: how to expense travel; Possible Parent Folder: "Employee Resources" or "Expenses".

        Respond with only the Parent Folder name and nothing else.

        {CONVO_STRUCTURE}

        Conversation:
        ###
        {conversation}
        ###
        """
    )

    openai_params = eave_openai.ChatCompletionParameters(
        model=eave_openai.OpenAIModel.GPT_35_TURBO_16K,
        messages=[prompt],
        n=1,
        frequency_penalty=0.9,
        presence_penalty=0.9,
        temperature=0,
    )

    answer: str | None = await eave_openai.chat_completion(openai_params)
    if answer is None:
        raise OpenAIDataError()

    parents = list(map(lambda x: x.strip(STRIPPED_CHARS), answer.split(",")))
    return parents


class DocumentationType(enum.Enum):
    TECHNICAL = "Technical Documentation"
    PROJECT = "Project One-Pager"
    TEAM_ONBOARDING = "Team Onboarding"
    ENGINEER_ONBOARDING = "Engineer Onboarding"
    UNKNOWN = "Other"


async def get_documentation_type(conversation: str) -> DocumentationType:
    prompt = eave_openai.formatprompt(
        f"""
        You know how to write the following types of documentation:

        - {DocumentationType.TECHNICAL.value}: This type of documentation is primarily used by engineers. It might describe how to setup a code repository, how to run tests, troubleshooting of local development environments, bug analysis, or other similar engineering tasks. It can also explain code, systems, architecture, and other engineering concerns.
        - {DocumentationType.PROJECT.value}: This type of documentation is used by both product managers and engineers. It might contain information about a project such as an overview, product features, tasks, questions, planning, estimated timeline, stakeholders, team members, and requirements.
        - {DocumentationType.TEAM_ONBOARDING.value}: This type of documentation is used by all new team members. It might contain information about the current team such as names, profile photos, and job titles. It can also list the team's preferred means of communication (for example, which Slack channels to use for different purposes), meeting schedule, and other information that the new team member needs to know to be successful on the team.
        - {DocumentationType.ENGINEER_ONBOARDING.value}: This type of documentation is used by engineers who are new to the team. It might contain a list of code repositories that the engineer should clone and setup, a list of requisite or optional software to install and how to install it, a description of the team's git workflow. It may also explain how to procure equipment or software from the company, such as a new keyboard, a different monitor, or a specific IDE.
        - {DocumentationType.UNKNOWN.value}: You can write any other type of documentation, but you prefer the types listed above when appropriate.\n

        Which of those types of documentation is most appropriate for the following conversation? Respond with just the type of documentation and nothing else.

        {CONVO_STRUCTURE}

        Conversation:
        ###
        {conversation}
        ###
        """
    )

    openai_params = eave_openai.ChatCompletionParameters(
        model=eave_openai.OpenAIModel.GPT_35_TURBO_16K,
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    if openai_response is None:
        raise OpenAIDataError()

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


async def get_documentation(
    conversation: str, documentation_type: DocumentationType, link_context: Optional[str]
) -> str:
    # TODO: Try getting headers first, then fill in the sections with separate prompts
    prompt_segments = []
    match documentation_type:
        case DocumentationType.TECHNICAL:
            prompt_segments.append(
                "Create Technical Documentation for the information in the following conversation. "
                "This documentation will be used primarily by software engineers."
            )
        case DocumentationType.PROJECT:
            prompt_segments.append(
                """
                Create a Project One-Pager document for the project being discussed in the following conversation.
                The document should be formatted as a table with the following headers: Category, Goal, Features, Notes.
                Each row in the table should describe details of a feature in the project.
                """
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
            prompt_segments.append("Create Documentation for the information in the following conversation.")

    prompt_segments.append(
        f"""
        You should not simply summarize the conversation; instead, you should extract information that is important, novel, and is likely to be valuable to other team members in the future.
        The documentation should be formatted using plain HTML tags without any inline styling. The documentation will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>.

        {CONVO_STRUCTURE}

        Conversation:
        ###
        {conversation}
        ###
        """,
    )

    if link_context:
        prompt_segments.append(
            f"""
            Use the information provided about the following links to help you write the documentation.

            ===
            {link_context}
            ===
            """,
        )

    prompt = eave_openai.formatprompt(*prompt_segments)

    openai_params = eave_openai.ChatCompletionParameters(
        model=eave_openai.OpenAIModel.GPT4,
        messages=[prompt],
        n=1,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        temperature=0.2,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params, baseTimeoutSeconds=120)
    if openai_response is None:
        raise OpenAIDataError()

    return openai_response
