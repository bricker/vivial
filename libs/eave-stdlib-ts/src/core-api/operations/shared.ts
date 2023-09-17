import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";

export const CORE_API_BASE_URL = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);
