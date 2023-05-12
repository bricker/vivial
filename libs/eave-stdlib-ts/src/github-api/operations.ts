import { Subscription } from '../core-api/models.js';

export namespace GetGithubUrlContent {
  export type RequestBody = {
    eaveTeamId: string;
    url: string;
  }

  export type ResponseBody = {
    content: string | null;
  }
}

export namespace CreateGithubResourceSubscription {
  export type RequestBody = {
    eaveTeamId: string;
    url: string;
  }

  export type ResponseBody = {
    subscription: Subscription | null;
  }
}