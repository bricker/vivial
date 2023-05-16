import asyncio
import enum
import re
from typing import Any, AsyncGenerator, List, Optional

import eave.pubsub_schemas
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
from eave.stdlib.exceptions import SlackDataError
import eave.stdlib.util as eave_util
import slack_sdk.errors
import slack_sdk.models.blocks
from eave.stdlib import logger
from pydantic import BaseModel, HttpUrl
from slack_bolt.async_app import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from .config import app_config


class _SlackContext:
    _context: AsyncBoltContext
    client: AsyncWebClient

    def __init__(self, context: AsyncBoltContext) -> None:
        self._context = context
        if context.client is None:
            raise SlackDataError("_SlackContext context.client")

        self.client = context.client


class SlackProfile:
    _ctx: _SlackContext
    title: str
    first_name: str
    last_name: str
    real_name: str
    real_name_normalized: str
    display_name: str
    display_name_normalized: str
    fields: dict[str, Any]
    status_text_canonical: str
    status_text: str
    status_emoji: str
    status_emoji_display_info: list[Any]
    status_expiration: int
    avatar_hash: str
    is_custom_image: Optional[bool]
    image_original: Optional[str]
    image_24: Optional[str]
    image_32: Optional[str]
    image_48: Optional[str]
    image_72: Optional[str]
    image_192: Optional[str]
    image_512: Optional[str]
    image_1024: Optional[str]

    always_active: Optional[bool]
    """Bot only"""
    api_app_id: Optional[str]
    """Bot only"""
    bot_id: Optional[str]
    """Bot only"""

    def __init__(self, json: dict[str, Any], ctx: _SlackContext, **kwargs: Any) -> None:
        self._ctx = ctx
        self.title = json["title"]
        self.first_name = json["first_name"]
        self.last_name = json["last_name"]
        self.real_name = json["real_name"]
        self.real_name_normalized = json["real_name_normalized"]
        self.display_name = json["display_name"]
        self.display_name_normalized = json["display_name_normalized"]
        self.fields = json["fields"]
        self.status_text_canonical = json["status_text_canonical"]
        self.status_text = json["status_text"]
        self.status_emoji = json["status_emoji"]
        self.status_emoji_display_info = json["status_emoji_display_info"]
        self.status_expiration = json["status_expiration"]
        self.avatar_hash = json["avatar_hash"]
        self.is_custom_image = json.get("is_custom_image")
        self.image_original = json.get("image_original")
        self.image_24 = json.get("image_24")
        self.image_32 = json.get("image_32")
        self.image_48 = json.get("image_48")
        self.image_72 = json.get("image_72")
        self.image_192 = json.get("image_192")
        self.image_512 = json.get("image_512")
        self.image_1024 = json.get("image_1024")

        self.always_active = json.get("always_active")
        self.api_app_id = json.get("api_app_id")
        self.bot_id = json.get("bot_id")

    @classmethod
    async def get(cls, user_id: str, ctx: _SlackContext) -> Optional["SlackProfile"]:
        response = await ctx.client.users_profile_get(user=user_id)
        json = response.get("profile")
        if json is None:
            return None

        profile = cls(json=json, ctx=ctx)
        return profile


class SlackConversationTopic:
    data: eave.stdlib.typing.JsonObject
    value: str
    creator: str
    last_set: int

    def __init__(self, json: eave.stdlib.typing.JsonObject) -> None:
        self.data = json
        self.value = json["value"]
        self.creator = json["creator"]
        self.last_set = json["last_set"]


class SlackConversation:
    _ctx: _SlackContext
    data: dict[str, Any]
    id: str
    name: str
    name_normalized: str
    topic: SlackConversationTopic
    purpose: SlackConversationTopic
    created: int
    updated: int
    creator: str
    context_team_id: str
    is_channel: bool
    is_group: bool
    is_im: bool
    is_mpim: bool
    is_archived: bool
    is_private: bool
    is_general: bool
    is_shared: bool
    is_org_shared: bool
    is_pending_ext_shared: bool
    is_ext_shared: bool
    shared_team_ids: list[str]
    pending_connected_team_ids: list[str]
    pending_shared: list[Any]
    parent_conversation: Any
    unlinked: int
    is_member: bool
    last_read: str
    previous_names: list[str]

    @classmethod
    async def get(cls, channel_id: str, ctx: _SlackContext) -> Optional["SlackConversation"]:
        response = await ctx.client.conversations_info(channel=channel_id)
        json = response.get("channel")
        if json is None:
            return None

        channel = cls(json=json, ctx=ctx)
        return channel

    def __init__(self, json: dict[str, Any], ctx: _SlackContext) -> None:
        self._ctx = ctx
        self.data = json
        self.id = json["id"]
        self.name = json["name"]
        self.name_normalized = json["name_normalized"]
        self.topic = SlackConversationTopic(json["topic"])
        self.purpose = SlackConversationTopic(json["purpose"])
        self.created = json["created"]
        self.updated = json["updated"]
        self.creator = json["creator"]
        self.context_team_id = json["context_team_id"]
        self.is_channel = json["is_channel"]
        self.is_group = json["is_group"]
        self.is_im = json["is_im"]
        self.is_mpim = json["is_mpim"]
        self.is_archived = json["is_archived"]
        self.is_private = json["is_private"]
        self.is_general = json["is_general"]
        self.is_shared = json["is_shared"]
        self.is_org_shared = json["is_org_shared"]
        self.is_pending_ext_shared = json["is_pending_ext_shared"]
        self.is_ext_shared = json["is_ext_shared"]
        self.shared_team_ids = json["shared_team_ids"]
        self.pending_connected_team_ids = json["pending_connected_team_ids"]
        self.pending_shared = json["pending_shared"]
        self.parent_conversation = json["parent_conversation"]
        self.unlinked = json["unlinked"]
        self.is_member = json["is_member"]
        self.last_read = json["last_read"]
        self.previous_names = json["previous_names"]


class SlackMessageLinkType(enum.Enum):
    @classmethod
    def all(cls) -> list["SlackMessageLinkType"]:
        return [
            cls.user,
            cls.channel,
            cls.subteam,
            cls.special,
            cls.url,
        ]

    user = enum.auto()
    channel = enum.auto()
    subteam = enum.auto()
    special = enum.auto()
    url = enum.auto()


class SlackReaction:
    name: Optional[str]
    users: Optional[list[str]]
    count: Optional[int]

    def __init__(self, data: eave.stdlib.typing.JsonObject) -> None:
        self.name = data.get("name")
        self.users = data.get("users")
        self.count = data.get("count")


class SlackPermalink(BaseModel):
    channel: str
    permalink: HttpUrl


class SlackMessage:
    """
    https://api.slack.com/events/message
    https://api.slack.com/reference/messaging/payload
    """

    _ctx: _SlackContext

    event: eave.stdlib.typing.JsonObject
    subtype: Optional[str]
    """https://api.slack.com/events/message#subtypes"""

    client_message_id: Optional[str]
    bot_id: Optional[str]
    app_id: Optional[str]
    bot_profile: Optional[eave.stdlib.typing.JsonObject]
    text: Optional[str]
    user: Optional[str]
    ts: str
    edited: Optional[eave.stdlib.typing.JsonObject]
    channel: Optional[str]
    blocks: Optional[list[Any]]
    team: Optional[str]
    thread_ts: Optional[str]
    reply_count: Optional[int]
    reply_users_count: Optional[int]
    latest_reply: Optional[str]
    reply_users: Optional[list[str]]
    is_locked: Optional[bool]
    subscribed: Optional[bool]
    reactions: Optional[list[SlackReaction]]

    # These properties are left intentionally uninitialized.
    # Call the respective get_*_mentions or expand_* methods to set the values.
    user_mentions: Optional[list[SlackProfile]] = None
    user_mentions_dict: Optional[dict[str, SlackProfile]] = None
    """user id -> user profile"""
    channel_mentions: Optional[list[SlackConversation]] = None
    channel_mentions_dict: Optional[dict[str, SlackConversation]] = None
    """channel id -> channel name"""
    subteam_mentions: Optional[list[str]] = None
    subteam_mentions_dict: Optional[dict[str, str]] = None
    """subteam id -> subteam name"""
    special_mentions: Optional[list[str]] = None
    special_mentions_dict: Optional[dict[str, str]] = None
    """special mention name -> special mention name"""
    urls: list[str]

    def __init__(
        self, data: eave.stdlib.typing.JsonObject, slack_context: AsyncBoltContext, channel: Optional[str] = None
    ) -> None:
        self._ctx = _SlackContext(context=slack_context)
        self.event = data
        self.subtype = data.get("subtype")
        self.client_message_id = data.get("client_message_id")
        self.bot_id = data.get("bot_id")
        self.app_id = data.get("app_id")
        self.bot_profile = data.get("bot_profile")
        self.text = data.get("text")
        self.user = data.get("user")
        self.ts = data["ts"]
        self.edited = data.get("edited")
        self.channel = channel if channel is not None else data.get("channel")
        self.blocks = data.get("blocks")
        self.team = data.get("team")
        self.thread_ts = data.get("thread_ts")
        self.reply_count = data.get("reply_count")
        self.reply_users_count = data.get("reply_users_count")
        self.latest_reply = data.get("latest_reply")
        self.reply_users = data.get("reply_users")
        self.is_locked = data.get("is_locked")
        self.subscribed = data.get("subscribed")
        self.reactions = data.get("reactions")

    @property
    def is_bot_message(self) -> bool:
        return self.bot_id is not None

    @property
    def is_debug(self) -> bool:
        if self.text is None:
            return False

        return re.search("^eavedebug:", self.text) is not None

    @property
    def guid(self) -> str:
        candidates = (
            self.team,
            self.channel,
            self.ts,
        )

        filtered = [e for e in candidates if e is not None]
        return "#".join(list(filtered))

    @property
    def subscription_id(self) -> str:
        candidates = (
            self.team,
            self.channel,
            self.parent_ts,
        )

        filtered = [e for e in candidates if e is not None]
        return "#".join(list(filtered))

    @property
    def is_threaded(self) -> bool:
        return self.thread_ts is not None

    @property
    def parent_ts(self) -> str:
        """
        For an unthreaded message, or a message that is a parent message of a thread,
        thread_ts and ts are the same value.
        """
        return self.thread_ts if self.thread_ts is not None else self.ts

    @property
    def text_without_leading_mention(self) -> str:
        """
        Removes @mentions from the beginning of the message.
        This is useful for matching against the substantial part of the message text
        Example:
            before: @Eave what time is it?
            after: what time is it?
        """
        if self.text is None:
            raise SlackDataError("message text")

        return re.sub("^(<@.+?>\\s?)+", "", self.text)

    @property
    def subscription_source(self) -> eave_models.SubscriptionSource:
        return eave_models.SubscriptionSource(
            platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.slack,
            event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.slack_message,
            id=self.subscription_id,
        )

    @property
    def is_eave(self) -> bool:
        v: bool = self.app_id == app_config.eave_slack_app_id
        return v

    async def send_response(
        self, text: Optional[str] = None, blocks: Optional[List[slack_sdk.models.blocks.Block]] = None
    ) -> None:
        if self.channel is None:
            raise SlackDataError("channel")

        if text is not None:
            msg = f"<@{self.user}> {text}"

            await self._ctx.client.chat_postMessage(
                channel=self.channel,
                text=msg,
                thread_ts=self.parent_ts,
            )

            return

    #         if blocks is not None:
    #             blocks.extend([
    #                 slack_sdk.models.blocks.DividerBlock(),
    #                 slack_sdk.models.blocks.ContextBlock(
    #                     elements=[
    # slack_sdk.models.blocks.basic_components.MarkdownTextObject(
    #                         text=f"*<{document_reference.document_url}|{document.title}>*\n{document.summary}",
    #                     ),
    #                     ]
    #                     text=
    #                 ),
    #             ])
    #             await eave.slack.client.chat_postMessage(
    #                 channel=self.message.channel,
    #                 blocks=blocks,
    #                 thread_ts=self.message.parent_ts,
    #             )
    #             return

    async def add_reaction(self, name: str) -> bool:
        if self.channel is None:
            raise SlackDataError("channel")
        if self.ts is None:
            raise SlackDataError("message ts")

        try:
            await self._ctx.client.reactions_add(name=name, channel=self.channel, timestamp=self.ts)
            return True
        except slack_sdk.errors.SlackApiError as e:
            # https://api.slack.com/methods/reactions.add#errors
            error_code = e.response.get("error")
            logger.warning(f"Error reacting to message: {error_code}", exc_info=e)
            return False

    @eave_util.memoized
    async def check_eave_is_mentioned(self) -> bool:
        await self.get_expanded_text()
        if self.user_mentions is None:
            return False
        value = any(profile.api_app_id == app_config.eave_slack_app_id for profile in self.user_mentions)
        return value

    @eave_util.memoized
    async def get_parent_permalink(self) -> SlackPermalink | None:
        if self.channel is None:
            return None

        response = await self._ctx.client.chat_getPermalink(
            channel=self.channel,
            message_ts=self.parent_ts,
        )

        channel = response.get("channel")
        permalink = response.get("permalink")

        if channel is None or permalink is None:
            return None

        return SlackPermalink.parse_obj(response.data)

    @eave_util.memoized
    async def get_permalink(self) -> SlackPermalink | None:
        if self.channel is None:
            return None

        response = await self._ctx.client.chat_getPermalink(
            channel=self.channel,
            message_ts=self.ts,
        )

        channel = response.get("channel")
        permalink = response.get("permalink")

        if channel is None or permalink is None:
            return None

        return SlackPermalink.parse_obj(response.data)

    @eave_util.memoized
    async def get_conversation_messages(self) -> list["SlackMessage"] | None:
        if self.channel is None:
            raise SlackDataError("channel")

        response = await self._ctx.client.conversations_replies(
            channel=self.channel,
            ts=self.parent_ts,
        )

        messages = response.get("messages")
        if messages is None:
            raise SlackDataError("conversation messages")

        # FIXME: This seems janky
        messages_list = [SlackMessage(m, slack_context=self._ctx._context) for m in messages]
        return messages_list

    async def formatted_messages(self) -> AsyncGenerator[str, None]:
        messages = await self.get_conversation_messages()
        if messages is None:
            return

        for message in messages:
            formatted_message = await message.get_formatted_message()
            if formatted_message is not None:
                yield formatted_message

    @eave_util.memoized
    async def get_formatted_conversation(self) -> str | None:
        messages = await self.get_conversation_messages()
        if messages is None:
            return None

        formatted_messages: list[Optional[str]] = await asyncio.gather(
            *[message.get_formatted_message() for message in messages]
        )

        filtered_messages = filter(None, formatted_messages)
        formatted_conversation = "\n".join(filtered_messages)
        return formatted_conversation

    @eave_util.memoized
    async def get_formatted_message(self) -> str | None:
        if self.is_bot_message:
            logger.debug("skipping bot message")
            return None

        expanded_text, user_profile = await asyncio.gather(
            self.get_expanded_text(),
            self.get_user_profile(),
        )

        if expanded_text is None or user_profile is None:
            logger.warning("expanded_text or user_profile were None")
            return None

        formatted_message = f"- Message from {user_profile.real_name}: {expanded_text}\n"
        return formatted_message

    @eave_util.memoized
    async def get_user_profile(self) -> SlackProfile | None:
        if self.user is None:
            return None

        profile = await SlackProfile.get(self.user, ctx=self._ctx)
        return profile

    @eave_util.memoized
    async def get_expanded_text(self) -> str | None:
        """
        Message text with links (user mentions, channels, subteams, special mentions, urls) replaced with real values.
        """

        if self.text is None:
            eave.stdlib.logger.warning("slack message text unexpectedly None")
            return None

        await asyncio.gather(
            self.resolve_user_mentions(),
            self.resolve_channel_mentions(),
            self.resolve_subteam_mentions(),
            self.resolve_special_mentions(),
            self.resolve_urls(),
        )

        expanded_text = self.text

        def replace_user_mention(match: re.Match[str]) -> str:
            if self.user_mentions_dict is None:
                return match.group()

            user_id = match.groups()[0]
            profile = self.user_mentions_dict.get(user_id)

            if profile is not None:
                return f"@{profile.real_name}"
            else:
                return match.group()

        expanded_text = re.sub("<@([UW]\\w+).*?>", replace_user_mention, expanded_text)

        def replace_channel_mention(match: re.Match[str]) -> str:
            if self.channel_mentions_dict is None:
                return match.group()

            groups = match.groups()
            channel_id = groups[0]

            channel = self.channel_mentions_dict.get(channel_id)

            if channel is not None and channel.name is not None:
                return f"@{channel.name}"
            else:
                return match.group()

        expanded_text = re.sub("<#(C\\w+).*?>", replace_channel_mention, expanded_text)

        def replace_subteam_mention(match: re.Match[str]) -> str:
            if self.subteam_mentions_dict is None:
                return match.group()

            id = match.groups()[0]
            obj = self.subteam_mentions_dict.get(id)

            if obj is not None:
                return f"@{obj}"
            else:
                return match.group()

        expanded_text = re.sub("<!subteam\\^(\\w+).*?>", replace_subteam_mention, expanded_text)

        def replace_special_mention(match: re.Match[str]) -> str:
            if self.special_mentions_dict is None:
                return match.group()

            id = match.groups()[0]
            obj = self.special_mentions_dict.get(id)

            if obj is not None:
                return f"@{obj}"
            else:
                return match.group()

        expanded_text = re.sub("<![(here)|(channel)|(everyone)]>", replace_special_mention, expanded_text)

        def replace_url(match: re.Match[str]) -> str:
            groups = match.groups()
            if len(groups) == 1:
                url = groups[0]
                return f"{url}"

            if len(groups) == 2:
                url = groups[0]
                name = groups[1]
                return f"{url} (link to {name})"

            return match.group()

        expanded_text = re.sub("<(.*?)\\|?(.*?)?>", replace_url, expanded_text)
        return expanded_text

    @eave_util.memoized
    async def resolve_user_mentions(self) -> None:
        links = self.parse_links()
        users = links[SlackMessageLinkType.user]

        user_mentions = list[SlackProfile]()
        user_mentions_dict = dict[str, SlackProfile]()

        for user_id in users:
            profile = await SlackProfile.get(user_id, ctx=self._ctx)
            if profile is not None:
                user_mentions.append(profile)
                user_mentions_dict[user_id] = profile

        self.user_mentions = user_mentions
        self.user_mentions_dict = user_mentions_dict

    @eave_util.memoized
    async def resolve_channel_mentions(self) -> None:
        links = self.parse_links()
        channels = links[SlackMessageLinkType.channel]

        channel_mentions = list[SlackConversation]()
        channel_mentions_dict = dict[str, SlackConversation]()

        for channel_id in channels:
            channel = await SlackConversation.get(channel_id, ctx=self._ctx)
            if channel is not None:
                channel_mentions.append(channel)
                channel_mentions_dict[channel_id] = channel

        self.channel_mentions = channel_mentions
        self.channel_mentions_dict = channel_mentions_dict

    @eave_util.memoized
    async def resolve_subteam_mentions(self) -> None:
        links = self.parse_links()
        subteams = links[SlackMessageLinkType.subteam]

        subteam_mentions = list[str]()
        subteam_mentions_dict = dict[str, str]()

        for subteam_id in subteams:
            # TODO: fetch subteam info from Slack API
            subteam_mentions.append(subteam_id)
            subteam_mentions_dict[subteam_id] = subteam_id

        self.subteam_mentions = subteam_mentions
        self.subteam_mentions_dict = subteam_mentions_dict

    @eave_util.memoized
    async def resolve_special_mentions(self) -> None:
        links = self.parse_links()
        specials = links[SlackMessageLinkType.special]

        self.special_mentions = specials
        self.special_mentions_dict = {value: value for value in specials}

    @eave_util.memoized
    async def resolve_urls(self) -> None:
        links = self.parse_links()
        urls = links[SlackMessageLinkType.url]
        self.urls = urls

    @eave_util.sync_memoized
    def parse_links(self) -> dict[SlackMessageLinkType, list[str]]:
        links = {
            SlackMessageLinkType.user: list[str](),
            SlackMessageLinkType.channel: list[str](),
            SlackMessageLinkType.subteam: list[str](),
            SlackMessageLinkType.special: list[str](),
            SlackMessageLinkType.url: list[str](),
        }

        if self.text is None:
            return links

        matches = re.finditer("<(.*?)>", self.text)

        for match in matches:
            link = match.groups()[0]

            user_match = re.match("^@([UW]\\w+)", link)
            if user_match is not None:
                links[SlackMessageLinkType.user].append(user_match.groups()[0])
                continue

            channel_match = re.match("^#(C\\w+)", link)
            if channel_match is not None:
                links[SlackMessageLinkType.channel].append(channel_match.groups()[0])
                continue

            subteam_match = re.match("^!subteam\\^(\\w+)", link)
            if subteam_match is not None:
                links[SlackMessageLinkType.subteam].append(subteam_match.groups()[0])
                continue

            special_match = re.match("^![(here)|(channel)|(everyone)]", link)
            if special_match is not None:
                links[SlackMessageLinkType.special].append(special_match.groups()[0])
                continue

            links[SlackMessageLinkType.url].append(link)

        return links

    @eave_util.memoized
    async def simple_format(self) -> str | None:
        if self.is_bot_message:
            logger.debug("skipping bot message")
            return None

        expanded_text, user_profile = await asyncio.gather(
            self.get_expanded_text(),
            self.get_user_profile(),
        )

        if expanded_text is None:
            raise SlackDataError("message expanded text")
        if user_profile is None:
            # FIXME: Maybe this will break for deactivated users?
            raise SlackDataError("message user profile")

        # TODO: Add job titles
        formatted_message = f"{user_profile.real_name}: {expanded_text}\n\n"
        return formatted_message

    @eave_util.memoized
    async def full_format(self) -> str | None:
        raise NotImplementedError


class SlackShortcut:
    pass

    # {
    # 'type': 'message_action',
    # 'token': 'DDbHGlwnoH4IfRkXGs7bEHzR',
    # 'action_ts': '1673216732.465751',
    # 'team': {
    #     'id': 'T03G5LV6R7Y',
    #     'domain': 'eave-fyi'
    # },
    # 'user':
    #     'id': 'U03H23466MN',
    #     'username': 'bryancricker',
    #     'team_id': 'T03G5LV6R7Y',
    #     'name': 'bryancricker'
    # },
    # 'channel': {
    #     'id': 'C04GDPU3B5Z',
    #     'name': 'bot-testing'
    # },
    # 'is_enterprise_install': False,
    # 'enterprise': None,
    # 'callback_id': 'eave_watch_request',
    # 'trigger_id': '4604390294198.3549709229270.0707da46b65bf66a1b303c03d64033c1',
    # 'response_url': 'https://hooks.slack.com/app/T03G5LV6R7Y/4613452039588/N1GxHXVWpEHqEuE6nOeJAGR7',
    # 'message_ts': '1673068010.394289',
    # 'message': {
    #     'client_msg_id': '6eb36e25-c4cc-4fe7-b858-668fa3b53907',
    #     'type': 'message',
    #     'text': '<@U03H23466MN> the logo you sent is too small for the website header, are you able to send an SVG?',
    #     'user': 'U03H23466MN',
    #     'ts': '1673068010.394289',
    #     'blocks': [
    #         {
    #             'type': 'rich_text',
    #             'block_id': 'CjH',
    #             'elements': [
    #                 {
    #                     'type': 'rich_text_section',
    #                     'elements': [
    #                         {
    #                             'type': 'user',
    #                             'user_id': 'U03H23466MN'
    #                         },
    #                         {
    #                             'type': 'text',
    #                             'text': ' the logo you sent is too small for the website header, are you able to send an SVG?'
    #                         }
    #                     ]
    #                 }
    #             ]
    #         }
    #     ],
    #     'team': 'T03G5LV6R7Y',
    #     'thread_ts': '1673068010.394289',
    #     'reply_count': 20,
    #     'reply_users_count': 2,
    #     'latest_reply': '1673214192.830519',
    #     'reply_users': [
    #         'U03H23466MN',
    #         'U04H28J3TCH'
    #     ],
    #     'is_locked': False,
    #     'subscribed': True,
    #     'last_read': '1673214192.830519'
    # }
