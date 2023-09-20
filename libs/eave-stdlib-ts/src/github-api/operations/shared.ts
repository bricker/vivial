import { Handler } from "express";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";
import { originMiddleware } from "../../middleware/origin.js";
import { signatureVerification } from "../../middleware/signature-verification.js";
import eaveHeaders from '../../headers.js';
import { requireHeaders } from "../../middleware/require-headers.js";
import { rawJsonBody } from "../../middleware/common-middlewares.js";
import { jsonParser } from "../../middleware/body-parser.js";
import { ServerApiEndpointConfiguration } from "../../api-util.js";
import { ExpressRoutingMethod } from "../../types.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app);

export class GithubAppEndpointConfiguration extends ServerApiEndpointConfiguration {
  get url(): string {
    return `${baseUrl}${this.path}`;
  }

  get middlewares(): Handler[] {
    const m: Handler[] = [];
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
