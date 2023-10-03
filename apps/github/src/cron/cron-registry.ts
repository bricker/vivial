import Express from "express";
import { runApiDocumentationCronHandler } from "./run-api-documentation-cron.js";

export function getCronHandler({
  dispatchKey,
}: {
  dispatchKey: string;
}): Express.Handler | undefined {
  // These keys correspond to the "eave-cron-dispatch-key" header
  // A dict isn't used to avoid remote-code execution type attacks, eg `cronRegistry[headerValue]`
  switch (dispatchKey) {
    case "run-api-documentation":
      return runApiDocumentationCronHandler;
    default:
      return undefined;
  }
}
