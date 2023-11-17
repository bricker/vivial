import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export type RunApiDocumentationTaskRequestBody = {
  repo: GithubRepoInput;
  force?: boolean;
};

export class RunApiDocumentationTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/_/github/tasks/run-api-documentation",
    authRequired: false,
  });

  /**
   * Performs an asynchronous operation by making a request with the provided arguments.
   *
   * @param args - An object that contains a team ID and an input of type RunApiDocumentationTaskRequestBody.
   * @returns A promise that resolves to void.
   *
   * @example
   * ```typescript
   * await perform({
   *   teamId: '123',
   *   input: {
   *     taskId: 'abc',
   *     document: 'xyz'
   *   }
   * });
   * ```
   */
  static async perform(
    args: RequestArgsTeamId & {
      input: RunApiDocumentationTaskRequestBody;
    },
  ): Promise<void> {
    await makeRequest({
      config: this.config,
      ...args,
    });
  }
}
