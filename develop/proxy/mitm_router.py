import logging
import re
import mitmproxy.http

class NoUpstreamDefinedError(Exception):
    pass

def request(flow: mitmproxy.http.HTTPFlow) -> None:
    if re.search(r"\.eave\.localhost$", flow.request.host) is None:
        # do nothing
        return

    if flow.request.host == "www.eave.localhost":
        port = 5000
    elif flow.request.host == "api.eave.localhost":
        port = 5100
    elif flow.request.host == "apps.eave.localhost" and re.match("/slack", flow.request.path):
        port = 5200
    elif flow.request.host == "apps.eave.localhost" and re.match("/github", flow.request.path):
        port = 5300
    else:
        flow.kill()
        raise NoUpstreamDefinedError(f"No upstream defined for {flow.request.url}")

    original_url = flow.request.url
    flow.request.scheme = "http"
    flow.request.port = port
    new_url = flow.request.url
    logging.info(f"Rewriting {original_url} to {new_url}")
