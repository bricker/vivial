import { EaveLogger } from "@eave-fyi/eave-collector-core";
import { LOG_TRACKER_URL, MODE } from "./compile-config";

export const logger = new EaveLogger({ logIngestUrl: LOG_TRACKER_URL, mode: MODE, clientId: TODO });
