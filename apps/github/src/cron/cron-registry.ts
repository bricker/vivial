import Express from "express";

export function getCronHandler({
  dispatchKey,
}: {
  dispatchKey: string;
}): Express.Handler | undefined {
  // These keys correspond to the "eave-cron-dispatch-key" header
  // A dict isn't used to avoid remote-code execution type attacks, eg `cronRegistry[headerValue]`
  switch (dispatchKey) {
    default:
      return undefined;
  }
}
