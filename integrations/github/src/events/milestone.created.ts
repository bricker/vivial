// import { MilestoneCreatedEvent } from '@octokit/webhooks-types';
// import { CreateIssueInput } from '@octokit/graphql-schema';
// import * as GraphQLUtil from '../graphql-util';
// import { GitHubOperationsContext } from '../types';

// export default async function handler(event: MilestoneCreatedEvent, context: GitHubOperationsContext) {
//   console.info('Processing milestone.created', event);

//   const label = await GraphQLUtil.getLabel('Epic', context);
//   const query = await GraphQLUtil.loadQuery('createIssue');
//   const input: CreateIssueInput = {
//     repositoryId: event.repository.node_id,
//     milestoneId: event.milestone.node_id,
//     title: event.milestone.title,
//     labelIds: label ? [label.id] : [],
//   };

//   await context.octokit.graphql(query, { input });
// }
