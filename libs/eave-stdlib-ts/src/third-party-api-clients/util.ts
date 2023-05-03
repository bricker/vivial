import { ApiClientBase } from '../third-party-api-clients/base';
import { GithubClient } from '../third-party-api-clients/github';
import { LinkType } from '../core-api/enums';


export type LinkContext = {
  url: string,
  type: LinkType,
  authData: any,
}

export function createClient(context: LinkContext): ApiClientBase {
  switch (context.type) {
    case LinkType.github:
      const installationId = context.authData;
      return new GithubClient(installationId);
  }
}