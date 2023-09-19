import { RequestHandler } from "express";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";
import { originMiddleware } from "../../middleware/origin.js";
import { signatureVerification } from "../../middleware/signature-verification.js";
import eaveHeaders from '../../headers.js';
import { requireHeaders } from "../../middleware/require-headers.js";
import { rawJsonBody } from "../../middleware/common-middlewares.js";
import { jsonParser } from "../../middleware/body-parser.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app);

export const GITHUB_APP_API_MOUNT_PATH = "/github/api"
export const GITHUB_APP_WEBHOOK_MOUNT_PATH = "/github/events"
export const GITHUB_APP_TASKS_MOUNT_PATH = "/_/github/tasks"

export class GithubAppEndpointConfiguration {
  mountPath: string;
  subPath: string;
  teamIdRequired: boolean;
  authRequired: boolean;
  originRequired: boolean;
  signatureRequired: boolean;

  constructor({
    mountPath,
    subPath,
    teamIdRequired = true,
    authRequired = true,
    originRequired = true,
    signatureRequired = true,
  }: {
    mountPath: string,
    subPath: string,
    teamIdRequired?: boolean,
    authRequired?: boolean,
    originRequired?: boolean,
    signatureRequired?: boolean,
  }) {
    this.mountPath = mountPath;
    this.subPath = subPath;
    this.teamIdRequired = teamIdRequired;
    this.authRequired = authRequired;
    this.originRequired = originRequired;
    this.signatureRequired = signatureRequired;
  }

  get url(): string {
    return `${baseUrl}${this.path}`;
  }

  get path(): string {
    return `${this.mountPath}${this.subPath}`;
  }

  get middlewares(): RequestHandler[] {
    const m: RequestHandler[] = [];
    const headers: string[] = [];

    m.push(rawJsonBody);

    if (this.originRequired) {
      headers.push(eaveHeaders.EAVE_ORIGIN_HEADER);
      m.push(originMiddleware);
    }
    if (this.teamIdRequired) {
      headers.push(eaveHeaders.EAVE_TEAM_ID_HEADER);
      // TODO: Team ID validation not implemented in TS apps
      // m.push();

    }
    if (this.authRequired) {
      headers.push(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
      // TODO: Auth not implemented in TS apps
      // m.push();
    }
    if (this.signatureRequired) {
      headers.push(eaveHeaders.EAVE_SIGNATURE_HEADER);
      m.push(signatureVerification());
    }

    m.unshift(requireHeaders(...headers));
    m.push(jsonParser);

    return m;
  }
}
