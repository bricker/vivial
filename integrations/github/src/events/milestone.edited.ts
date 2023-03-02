// import { MilestoneEditedEvent } from '@octokit/webhooks-types';
// import { Query, Issue, UpdateIssueInput, IssueFilters, Scalars, Milestone, Maybe } from '@octokit/graphql-schema';
// import * as GraphQLUtil from '../graphql-util';
// import { GitHubOperationsContext } from '../types';

// export default async function handler(event: MilestoneEditedEvent, context: GitHubOperationsContext) {
//   console.info('Processing milestone.edited', event);

//   const epicIssue = await getEpicIssue(event.milestone.node_id, context);
//   if (!epicIssue) {
//     console.info('No issue found with Epic label for Milestone', event.milestone.node_id);
//     return;
//   }

//   const query = await GraphQLUtil.loadQuery('updateIssue');
//   const input: UpdateIssueInput = {
//     id: epicIssue.id,
//     title: event.milestone.title,
//   };

//   await context.octokit.graphql(query, { input });
// }

// async function getEpicIssue(milestoneNodeId: string, context: GitHubOperationsContext): Promise<Maybe<Issue> | undefined> {
//   const query = await GraphQLUtil.loadQuery('getMilestoneIssues');
//   const variables: { milestoneNodeId: Scalars['ID'], first: Scalars['Int'], issueFilters: IssueFilters } = {
//     milestoneNodeId,
//     first: 1,
//     issueFilters: {
//       labels: ['Epic'],
//     },
//   };

//   const response = await context.octokit.graphql<{ node: Query['node'] }>(query, variables);
//   const milestone = <Milestone>response.node;
//   const epicIssue = milestone.issues.nodes?.at(0);
//   return epicIssue;
// }
