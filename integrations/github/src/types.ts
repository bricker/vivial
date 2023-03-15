import { Octokit } from 'octokit';

export declare type GitHubOperationsContext = {
  octokit: Octokit
}

export declare type JsonValue =
  string |
  number |
  null |
  string[] |
  number[] |
  null[] |
  {[key: string]: JsonValue} |
  {[key: string]: JsonValue}[];
