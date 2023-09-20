import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { Octokit } from 'octokit';

export type GitHubOperationsContext = {
  octokit: Octokit;
  ctx: LogContext;
};
