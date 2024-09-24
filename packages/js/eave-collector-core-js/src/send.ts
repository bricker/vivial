import { Logger } from "./logging/types";

export function sendWithClientId({
  jsonBody,
  url,
  clientId,
  logger = console,
}: {
  jsonBody: object;
  url: string;
  clientId: string;
  logger?: Logger;
}) {
  try {
    const json = JSON.stringify(jsonBody);

    logger.debug("Sending data", json);

    fetch(`${url}?clientId=${clientId}`, {
      method: "POST",
      headers: {
        // Important note: The Content-Type should be `application/x-www-form-urlencoded`,
        // because that mimetype is CORS-safelisted as documented here:
        // https://fetch.spec.whatwg.org/#cors-safelisted-request-header
        // If set to a non-safe mimetype (eg application/json), fetch will send a pre-flight CORS request (OPTIONS)
        // to the server, and the server is then responsible for responding with CORS "access-control-allow-*" headers.
        // That's okay, but it adds unnecessary overhead to both the client and the server.
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: json,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Network response ${response.status}`);
        }
      })
      .catch((error) => {
        logger.error("Error sending data", error);
      });
  } catch (e) {
    logger.error(e);
    return;
  }
}
