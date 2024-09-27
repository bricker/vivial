import { EaveLogger } from "@eave-fyi/eave-collector-core";
import { EAVE_CLIENT_ID, LOG_TRACKER_URL, MODE } from "./compile-config";

export const logger = new EaveLogger({
  tag: "eave-collector-browser-js",
  logIngestUrl: LOG_TRACKER_URL,
  mode: MODE,
  clientId: EAVE_CLIENT_ID,
});
