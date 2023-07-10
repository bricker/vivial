import { PullRequestEvent } from '@octokit/webhooks-types';
import { GitHubOperationsContext } from '../types.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { appConfig } from '../config.js';
import { getGithubInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js';

// TODO: move elsewhere
type GithubFile = {
  filename: String,
  contents_url: String,
}


/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 * 
 * Features:
 * Checks if closed PR was merged. If so, update inline file docs
 * for each file with code changes. 
 */
export default async function handler(event: PullRequestEvent, context: GitHubOperationsContext) {
  // verify PR was closed and merged
  if (event.action !== 'closed' || !event.pull_request.merged) {
    return;
  }

  const { ctx, octokit } = context;
  eaveLogger.debug('Processing push', ctx);

  // find files changed in PR commits
  let page = 1;
  const pageSize = 50;
  let keepPaginating = true;
  let files: Array<GithubFile> = [];

  while (keepPaginating) {
    // fetch paginated list of files
    // Note: Responses include a maximum of 3000 files. 
    // https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests-files
    let { data: filesResp } = await octokit.rest.pulls.listFiles({
      per_page: pageSize,
      page,
      owner: event.repository.owner.name,
      repo: event.repository.name,
      pull_number: event.pull_request.number,
    });

    // extract files that were changed
    const documentableFiles = filesResp.filter((f) => f.status === 'added' || f.status === 'changed' || f.status === 'modified');

    // TODO: extract files that we want comments in

    // convert api resp to GithubFile type (?)
    files = files.concat(documentableFiles);

    // continue while files fill page size
    keepPaginating = filesResp.length === pageSize;
  }


  // update docs in each file
  const openaiClient = await OpenAIClient.getAuthedClient();


  // branch off event.pull_request.base branch

  // commit changes

  // open PR against event.pull_request.base branch


}