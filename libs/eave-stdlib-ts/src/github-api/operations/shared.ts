import { Handler } from "express";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";
import { originMiddleware } from "../../middleware/origin.js";
import { signatureVerification } from "../../middleware/signature-verification.js";
import { requireHeaders } from "../../middleware/require-headers.js";
import { rawJsonBody } from "../../middleware/common-middlewares.js";
import { jsonParser } from "../../middleware/body-parser.js";
import { ServerApiEndpointConfiguration } from "../../api-util.js";
import { ExpressRoutingMethod } from "../../types.js";
import { EAVE_ACCOUNT_ID_HEADER, EAVE_ORIGIN_HEADER, EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER } from "../../headers.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app);

export class GithubAppEndpointConfiguration extends ServerApiEndpointConfiguration {
  audience = EaveApp.eave_github_app;

  get url(): string {
    return `${baseUrl}${this.path}`;
  }

  get middlewares(): Handler[] {
    const m: Handler[] = [];
    const headers: string[] = [];

    m.push(rawJsonBody);

    if (this.originRequired) {
      m.push(originMiddleware);
    }
    if (this.teamIdRequired) {
      headers.push(EAVE_TEAM_ID_HEADER);
      // TODO: Team ID validation not implemented in TS apps
      // m.push();
    }
    if (this.authRequired) {
      headers.push(EAVE_ACCOUNT_ID_HEADER);
      // TODO: Auth not implemented in TS apps
      // m.push();
    }
    if (this.signatureRequired) {
      m.push(signatureVerification({ audience: this.audience }));
    }

    m.unshift(requireHeaders(...headers));
    m.push(jsonParser);

    return m;
  }
}
