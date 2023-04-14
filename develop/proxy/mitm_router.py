import logging
import re

class NoUpstreamDefinedError(Exception):
    pass

def request(flow) -> None:
    if re.search(r"\.eave\.run$", flow.request.host) is None:
        # do nothing
        return

    if flow.request.host == "www.eave.run":
        port = 5000
    elif flow.request.host == "api.eave.run":
        port = 5100
    elif flow.request.host == "apps.eave.run" and re.match("/slack", flow.request.path):
        port = 5200
    elif flow.request.host == "apps.eave.run" and re.match("/github", flow.request.path):
        port = 5300
    else:
        flow.kill()
        raise NoUpstreamDefinedError(f"No upstream defined for {flow.request.url}")

    target = flow.request.host_header
    original_url = flow.request.url

    flow.request.scheme = "http"
    flow.request.headers["host"] = target
    flow.request.host = "127.0.0.1"
    flow.request.port = port
    new_url = flow.request.url

    logging.info(f"Rewriting {original_url} to {new_url}")
