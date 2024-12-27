import logging
import re

import mitmproxy.http


class NoUpstreamDefinedError(Exception):
    pass


class PrivateEndpointAccessError(Exception):
    pass


def request(flow: mitmproxy.http.HTTPFlow) -> None:
    if re.search(r"\.eave\.", flow.request.host) is None:
        flow.kill()
        raise NoUpstreamDefinedError(f"Unsupported domain: {flow.request.url}")

    is_internal = re.search(r"\.internal\.eave\.", flow.request.host)
    is_public = not is_internal

    if is_public:
        flow.request.headers["eave-lb"] = "1"

    # tld = flow.request.host.split(".")[-1]
    port = None

    if re.match(r"^www\.", flow.request.host):
        port = 5101

    elif re.match(r"^(core-)?api\.", flow.request.host):
        # Simulate Ingress rules. This should match the Core API Kubernetes Ingress configuration.
        if is_public:
            if len(flow.request.path_components) == 0 or flow.request.path_components[0] not in [
                "status",
                "healthz",
                "graphql",
                "public",
                "favicon.ico",
            ]:
                # The first path component is not whitelisted as a public endpoint.
                # In the real world, this would return something like a 404.
                flow.response = mitmproxy.http.Response.make(
                    404,
                    b"Private endpoints can't be accessed through public DNS. Use '.internal.eave.run' to simulate internal DNS.",
                    {"Content-Type": "text/plain"},
                )
                flow.kill()
        port = 5100

    elif re.match(r"^admin\.", flow.request.host):
        port = 5200
        if is_public:
            flow.response = mitmproxy.http.Response.make(
                404,
                b"Admin dash can't be accessed through public DNS. Use '.internal.eave.run' to simulate internal DNS.",
                {"Content-Type": "text/plain"},
            )
            flow.kill()

    elif re.match(r"^cdn\.", flow.request.host):
        # This is the port for a webpack server.
        port = 3001

    if not port:
        flow.kill()
        raise NoUpstreamDefinedError(f"No upstream defined for {flow.request.url}")

    original_url = flow.request.url
    flow.request.host = "127.0.0.1"
    flow.request.scheme = "http"
    flow.request.port = port
    new_url = flow.request.url
    logging.info(f"Rewriting {original_url} to {new_url}")
