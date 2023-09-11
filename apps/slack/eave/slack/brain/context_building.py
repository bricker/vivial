import asyncio
from typing import Optional
from eave.stdlib.transformer_ai import token_counter
import eave.stdlib.transformer_ai.openai_client as openai
import eave.stdlib.transformer_ai.models as ai_model
from eave.stdlib.util import memoized
from eave.stdlib import link_handler
from eave.stdlib.exceptions import SlackDataError
from .base import Base
from . import message_prompts
from ..config import app_config

context_building_model = ai_model.OpenAIModel.GPT4

class ContextBuildingMixin(Base):
    async def build_message_context(self) -> None:
        context: str = ""

        if self.user_profile is not None:
            caller_name = self.user_profile.real_name_normalized
            caller_job_title = self.user_profile.title

            context += f"from {caller_name}"
            if caller_job_title:  # might be empty string
                # context += f" ({caller_job_title})"
                pass

        # f"The question was asked in a Slack channel called \"\". "
        # f"The description of that channel is: \"\" "

        message_context = openai.formatprompt(
            f"""
            Message {context}:
            ###
            {self.expanded_text}
            ###
            """,
        )

        self.message_context = message_context

    @memoized
    async def build_context(self) -> str:
        context = await self.build_concatenated_context()
        if openai.token_count(data=context, model=context_building_model) > (ai_model.MAX_TOKENS[context_building_model] / 2):
            context = await self.build_rolling_context()

        return context

    async def build_concatenated_context(self) -> str:
        messages = await self.message.get_conversation_messages()
        if messages is None:
            raise SlackDataError("messages for concatenated context")

        messages_without_self = filter(lambda m: m.is_eave is False, messages)

        formatted_messages: list[Optional[str]] = await asyncio.gather(
            *[message.simple_format() for message in messages_without_self]
        )

        filtered_messages = filter(None, formatted_messages)
        formatted_conversation = "\n".join(filtered_messages)

        # TODO: Add in reactions
        return formatted_conversation

    async def build_rolling_context(self) -> str:
        messages = await self.message.get_conversation_messages()
        if messages is None:
            raise SlackDataError("messages for rolling context")

        messages_without_self = filter(lambda m: m.is_eave is False, messages)

        messages_for_prompt = list[str]()
        total_tokens = 0

        condensed_context = ""

        for thread_message in messages_without_self:
            formatted_text = await thread_message.simple_format()
            if formatted_text is None:
                continue

            total_tokens += openai.token_count(data=formatted_text, model=context_building_model)

            if total_tokens > (ai_model.MAX_TOKENS[context_building_model] / 2):
                joined_messages = "\n\n".join(messages_for_prompt)
                prompt = openai.formatprompt(
                    f"""
                    Condense the following conversation in a way that maintains the important information, but removes anything off-topic or insubstantial.

                    {message_prompts.CONVO_STRUCTURE}

                    Conversation:
                    ###
                    {condensed_context}

                    {joined_messages}
                    ###
                    """
                )
                openai_params = openai.ChatCompletionParameters(
                    model=context_building_model,
                    messages=[prompt],
                    temperature=0.1,
                    frequency_penalty=1.0,
                    presence_penalty=1.0,
                )
                condensed_context = await openai.chat_completion(params=openai_params, ctx=self.eave_ctx)
                total_tokens = 0
                messages_for_prompt.clear()

            messages_for_prompt.append(formatted_text)

        recent_messages = "\n\n".join(messages_for_prompt)
        return f"{condensed_context}\n\n" f"{recent_messages}"


    async def _summarize_content(self, content: str) -> str:
        """
        Given some content (from a URL) return a summary of it.
        """
        if token_counter.token_count(data=content, model=context_building_model) > ai_model.MAX_TOKENS[context_building_model]:
            # build rolling summary of long content
            threshold = int(ai_model.MAX_TOKENS[context_building_model] / 2)
            return await self._rolling_summarize_content(content, threshold)
        else:
            prompt = openai.formatprompt(
                f"""
                Summarize the following information. Maintain the important information.

                ###

                {content}

                ###
                """
            )
            openai_params = openai.ChatCompletionParameters(
                model=context_building_model,
                messages=[prompt],
                temperature=0.9,
                frequency_penalty=1.0,
                presence_penalty=1.0,
            )
            summary_resp = await openai.chat_completion(params=openai_params, ctx=self.eave_ctx)
            return summary_resp

    async def _rolling_summarize_content(self, content: str, threshold: int) -> str:
        """
        Given a `content` string to summarize that is (assumed) longer than `threshold`
        tokens (as defined by the AI model), break `content` into digestable chunks,
        summarizing and integrating each chunk into a single "rolling" summary.

        content -- raw text to summarize. Presumed to long to summarize in 1 AI API request.
        threshold -- max number of tokens to feed to AI per request. (Recommended to be less than MAX_TOKENS allowed by API)
        """
        summary = content

        while openai.token_count(data=summary, model=context_building_model) > threshold:
            new_summary = ""
            chunk_size = threshold
            current_position = 0
            current_chunk = summary[current_position : current_position + chunk_size]
            chunks = [current_chunk]
            # there are generally 0.75 words per token, so approximating 1 character per token may
            # be overly generous in some contexts, but it's a safe minimum
            while len(current_chunk) == chunk_size:
                current_position += chunk_size
                current_chunk = summary[current_position : current_position + chunk_size]
                chunks.append(current_chunk)

            # summarize each chunk, combining it into existing summary
            for chunk in filter(lambda chunk: len(chunk) > 0, chunks):
                if new_summary == "":
                    prompt = openai.formatprompt(
                        f"""
                        Condense the following information. Maintain the important information.

                        ###
                        {chunk}
                        ###
                        """
                    )
                    openai_params = openai.ChatCompletionParameters(
                        model=context_building_model,
                        messages=[prompt],
                        temperature=0.9,
                        frequency_penalty=1.0,
                        presence_penalty=1.0,
                    )
                    new_summary = await openai.chat_completion(params=openai_params, ctx=self.eave_ctx)
                else:
                    prompt = openai.formatprompt(
                        f"""
                        Amend and expand on the following information. Maintain the important information.

                        ###
                        {new_summary}

                        {chunk}
                        ###
                        """
                    )
                    openai_params = openai.ChatCompletionParameters(
                        model=context_building_model,
                        messages=[prompt],
                        temperature=0.9,
                        frequency_penalty=1.0,
                        presence_penalty=1.0,
                    )
                    new_summary = await openai.chat_completion(params=openai_params, ctx=self.eave_ctx)
            summary = new_summary

        return summary


    async def build_link_context_and_subscribe(self) -> Optional[str]:
        """
        If there are any URL links in the message thread being analyzed,
        it pulls the context from the links (if Eave has access) and summarizes it.
        It then subscribes to watch for changes any files Eave could read.

        Returns summarized context for each link in message thread, if any
        """
        # see if we can pull content from any links in messages from the thread
        urls = [await msg.resolve_urls() for msg in await self.message.get_conversation_messages()]
        # flatten
        urls = [url for url_list in urls for url in url_list]
        supported_links = link_handler.filter_supported_links(urls)

        if supported_links:
            links_contents = await link_handler.map_url_content(origin=app_config.eave_origin, eave_team_id=self.eave_team.id, urls=supported_links)
            if links_contents:
                # summarize the content at each link, or None where link content wasnt obtained
                summaries: list[Optional[str]] = await asyncio.gather(
                    *[
                        # sleep(0) as a no-op returning None to preserve output len/ordering
                        asyncio.ensure_future(self._summarize_content(content)) if content else asyncio.sleep(0)
                        for content in links_contents
                        if content is not None
                    ]
                )

                # subscribe Eave to any changes at the links we were able to read content from
                link_subscriptions = await link_handler.subscribe_to_file_changes(
                    origin=app_config.eave_origin,
                    eave_team_id=self.eave_team.id,
                    urls=[link_info for link_info, content in zip(supported_links, summaries) if content is not None],
                )
                self.subscriptions += link_subscriptions

                # transform raw source text into less distracting (for AI) summaries
                return "\n\n".join(
                    [
                        f"""
                        {link}
                        ###
                        {summary}
                        ###
                        """
                        for (link, _), summary in zip(supported_links, summaries)
                        if summary is not None
                    ]
                )

        return None
