from eave.stdlib.slack_api import SlackAppEndpoint, SlackAppEndpointConfiguration


class SlackEventProcessorTaskOperation(SlackAppEndpoint):
    config = SlackAppEndpointConfiguration(
        path="/_/slack/tasks/events",
        method="POST",
        team_id_required=False,
        auth_required=False,
    )


class SlackWebhookOperation(SlackAppEndpoint):
    config = SlackAppEndpointConfiguration(
        path="/slack/events",
        method="POST",
        team_id_required=False,
        auth_required=False,
        signature_required=False,
        origin_required=False,
    )
