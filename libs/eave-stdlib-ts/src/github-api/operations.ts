import { Subscription } from '../core-api/models.js';

export namespace GetGithubLinkContent {
  export type RequestBody = {
    links: Array<string>;
  }

  export type ResponseBody = {
    subscriptions: Array<Subscription>;
    contents: Array<string>;
  }
}