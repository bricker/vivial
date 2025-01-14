# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.constants import EAVE_HOME
from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import os
import enum
from subprocess import PIPE, Popen

from slack_sdk.models.blocks import HeaderBlock, RichTextBlock, RichTextElementParts, RichTextListElement, RichTextSectionElement


from eave.stdlib.slack import get_authenticated_eave_system_slack_client



import asyncio
import click


_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID = os.getenv("SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID", "C086TDX5079") # notif-deployments

@click.group()
def cli() -> None:
    pass

@cli.group()
def deploy() -> None:
    pass

class DeploymentStatus(enum.StrEnum):
    IN_PROGRESS = enum.auto()
    COMPLETE = enum.auto()
    FAILED = enum.auto()

@deploy.command()
@click.option("-a", "--app", required=True)
@click.option("-s", "--status", required=True, type=click.Choice(list(DeploymentStatus), case_sensitive=False))
@click.option("-m", "--msg-timestamp", required=False)
@click.option("-c", "--cwd", required=False)
def notify_slack(app: str, status: DeploymentStatus, msg_timestamp: str | None, cwd: str | None) -> None:
    slack_client = get_authenticated_eave_system_slack_client()

    async def _post_message() -> None:
        assert slack_client

        if status == DeploymentStatus.IN_PROGRESS:
            p = Popen(["./bin/func", "e.diff-deployed"], cwd=cwd if cwd else None, env=os.environ, shell=False, stdout=PIPE)  # noqa: ASYNC220, S603
            stdout, stderr = p.communicate()
            changelog = stdout.decode()
            lines = changelog.splitlines()

            slack_response = await slack_client.chat_postMessage(
                channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                link_names=True,
                unfurl_links=False,
                unfurl_media=False,
                text=f"Deployment to *{app}* has started.\n\n{changelog}",
                blocks=[
                    HeaderBlock(
                        text=f"Deployment to {app} has started.",
                    ),
                    RichTextBlock(
                        elements=[
                            RichTextListElement(
                                style="bullet",
                                elements=[
                                    RichTextSectionElement(
                                        elements=[
                                            RichTextElementParts.Text(
                                                text=line,
                                                # style=RichTextElementParts.TextStyle(),
                                            )
                                        ]
                                    )
                                    for line in lines
                                ],
                            ),
                        ],
                    ),
                ],
            )

            await slack_client.reactions_add(
                channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                timestamp=slack_response["ts"],
                name="clock5",
            )

            click.echo(slack_response["ts"])

        else:
            assert msg_timestamp

            await slack_client.reactions_remove(
                channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                timestamp=msg_timestamp,
                name="clock5",
            )

            if status == DeploymentStatus.COMPLETE:
                await slack_client.reactions_add(
                    channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                    timestamp=msg_timestamp,
                    name="white_check_mark",
                )

                await slack_client.chat_postMessage(
                    channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                    thread_ts=msg_timestamp,
                    link_names=True,
                    text="Deployment Complete!",
                    unfurl_links=False,
                    unfurl_media=False,
                )

            elif status == DeploymentStatus.FAILED:
                await slack_client.reactions_add(
                    channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                    timestamp=msg_timestamp,
                    name="x",
                )

                await slack_client.chat_postMessage(
                    channel=_SLACK_DEPLOYMENT_NOTIFICATIONS_CHANNEL_ID,
                    thread_ts=msg_timestamp,
                    link_names=True,
                    text="Deployment Failed!",
                    unfurl_links=False,
                    unfurl_media=False,
                )

    if slack_client:
        asyncio.run(_post_message())

if __name__ == "__main__":
    cli()
