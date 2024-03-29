import logging
import re
import mitmproxy.http


class NoUpstreamDefinedError(Exception):
    pass


def request(flow: mitmproxy.http.HTTPFlow) -> None:
    if re.search(r"\.eave\.(localhost|run)$", flow.request.host) is None:
        # do nothing
        return

    # tld = flow.request.host.split(".")[-1]
    port = None

    if re.match(r"^dashboard\.", flow.request.host):
        port = 5000
    elif re.match(r"^api\.", flow.request.host):
        port = 5100
    elif re.match(r"^metabase\.", flow.request.host):
        port = 5400
    elif re.match(r"^apps\.", flow.request.host):
        if re.match(r"(/_)?/github", flow.request.path):
            port = 5300

    if not port:
        flow.kill()
        raise NoUpstreamDefinedError(f"No upstream defined for {flow.request.url}")

    original_url = flow.request.url
    flow.request.scheme = "http"
    flow.request.port = port
    new_url = flow.request.url
    logging.info(f"Rewriting {original_url} to {new_url}")
