import logging
import re

import mitmproxy.http


class NoUpstreamDefinedError(Exception):
    pass


class PrivateEndpointAccessError(Exception):
    pass


def request(flow: mitmproxy.http.HTTPFlow) -> None:
    if re.search(r"\.eave\.(localhost|run)$", flow.request.host) is None:
        # do nothing
        return

    is_internal = re.search(r"\.internal\.eave\.", flow.request.host)
    is_public = not is_internal

    if is_public:
        flow.request.headers["eave-lb"] = "1"

    # tld = flow.request.host.split(".")[-1]
    port = None

    if re.match(r"^dashboard\.", flow.request.host):
        port = 5000

    elif re.match(r"^(core-)?api\.", flow.request.host):
        # Simulate Ingress rules. This should match the Core API Kubernetes Ingress configuration.
        if is_public:
            if len(flow.request.path_components) == 0 or flow.request.path_components[0] not in [
                "status",
                "healthz",
                "public",
                "oauth",
                "favicon.ico",
            ]:
                # The first path component is not whitelisted as a public endpoint.
                # In the real world, this would return something like a 404.
                flow.kill()
                raise PrivateEndpointAccessError(
                    "Private endpoints can't be accessed through public DNS. Use '.internal.eave.run' to simulate internal DNS."
                )
        port = 5100

    elif re.match(r"^cdn\.", flow.request.host):
        # This is the port for a webpack server.
        port = 3001

    if not port:
        flow.kill()
        raise NoUpstreamDefinedError(f"No upstream defined for {flow.request.url}")

    original_url = flow.request.url
    flow.request.scheme = "http"
    flow.request.port = port
    new_url = flow.request.url
    logging.info(f"Rewriting {original_url} to {new_url}")
