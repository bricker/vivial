type Logger = {
  debug: (...args: any[]) => void;
  info: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  error: (...args: any[]) => void;
};

export function sendBeaconWithEaveAuth({
  jsonBody,
  url,
  logger = console,
}: {
  jsonBody: object;
  url: string;
  logger?: Logger;
}) {
  try {
    // @ts-ignore: todo, idk this was giving an error
    chrome.storage.local.get("EAVE_CLIENT_ID").then(({ EAVE_CLIENT_ID }: { EAVE_CLIENT_ID?: string }) => {
      if (!EAVE_CLIENT_ID) {
        logger.warn("EAVE_CLIENT_ID not set");
        return;
      }

      const json = JSON.stringify(jsonBody);

      // Important note: The `type` property here should be `application/x-www-form-urlencoded`, because that mimetype is CORS-safelisted as documented here:
      // https://fetch.spec.whatwg.org/#cors-safelisted-request-header
      // If set to a non-safe mimetype (eg application/json), sendBeacon will send a pre-flight CORS request (OPTIONS) to the server, and the server is then responsible
      // for responding with CORS "access-control-allow-*" headers. That's okay, but it adds unnecessary overhead to both the client and the server.
      const blob = new Blob([json], {
        type: "application/x-www-form-urlencoded; charset=UTF-8",
      });

      logger.debug("Sending beacon", json);

      const success = navigator.sendBeacon(`${url}?clientId=${EAVE_CLIENT_ID}`, blob);

      if (!success) {
        logger.warn("Failed to send beacon.");
        return;
      }
    }).catch((e: any) => {
      console.error(e);
    });
  } catch (e) {
    logger.error(e);
    return;
  }
}
