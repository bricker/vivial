import { EaveRequestState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import { Octokit } from 'octokit';

export declare type GitHubOperationsContext = {
  octokit: Octokit;
  eaveState: EaveRequestState;
};
