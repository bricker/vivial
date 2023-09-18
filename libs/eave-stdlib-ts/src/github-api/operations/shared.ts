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

export class GithubAppEndpointConfiguration {
  path: string;
  teamIdRequired: boolean;
  authRequired: boolean;
  originRequired: boolean;
  signatureRequired: boolean;

  constructor({
    path,
    teamIdRequired = true,
    authRequired = true,
    originRequired = true,
    signatureRequired = true,
  }: {
    path: string,
    teamIdRequired?: boolean,
    authRequired?: boolean,
    originRequired?: boolean,
    signatureRequired?: boolean,
  }) {
    this.path = path;
    this.teamIdRequired = teamIdRequired;
    this.authRequired = authRequired;
    this.originRequired = originRequired;
    this.signatureRequired = signatureRequired;
  }

  get url(): string {
    return `${baseUrl}${this.path}`;
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
