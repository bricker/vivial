import { EaveLogger } from "@eave-fyi/eave-collector-core";
import { LOG_TRACKER_URL, MODE } from "./compile-config";

export const logger = new EaveLogger({
  tag: "eave-collector-extension-js",
  logIngestUrl: LOG_TRACKER_URL,
  mode: MODE,
  clientId: "TODO",
});
