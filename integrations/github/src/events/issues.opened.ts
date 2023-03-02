// import { IssuesOpenedEvent } from '@octokit/webhooks-types';
// import { Mutation, AddProjectV2ItemByIdInput, ProjectV2Item } from '@octokit/graphql-schema';
// import * as Constants from '../../settings';
// import * as GraphQLUtil from '../graphql-util';
// import { GitHubOperationsContext } from '../types';

// export default async function handler(event: IssuesOpenedEvent, context: GitHubOperationsContext) {
//   console.info('Processing issues.opened', event);

//   await addIssueToProject(event.issue.node_id, context);
// }

// async function addIssueToProject(issueNodeId: string, context: GitHubOperationsContext): Promise<ProjectV2Item> {
//   const query = await GraphQLUtil.loadQuery('addProjectV2ItemById');
//   const input: AddProjectV2ItemByIdInput = {
//     contentId: issueNodeId,
//     projectId: Constants.GITHUB_PROJECT_ID,
//   };

//   const response = await context.octokit.graphql<{ addProjectV2ItemById: Mutation['addProjectV2ItemById'] }>(query, { input });
//   const item = response.addProjectV2ItemById!.item!;
//   return item;
// }
