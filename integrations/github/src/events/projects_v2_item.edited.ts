// import { ProjectsV2ItemEditedEvent } from '@octokit/webhooks-types';
// import { ProjectV2ItemFieldSingleSelectValue, Issue, UpdateIssueInput } from '@octokit/graphql-schema';
// import * as Constants from '../../settings';
// import * as GraphQLUtil from '../graphql-util';
// import { GitHubOperationsContext } from '../types';

// export default async function handler(event: ProjectsV2ItemEditedEvent, context: GitHubOperationsContext) {
//   console.info('Processing projects_v2_item.edited', event);

//   const {
//     changes,
//     projects_v2_item: {
//       node_id: itemNodeId,
//     },
//   } = event;

//   switch (changes.field_value.field_node_id) {
//     case Constants.STATUS_FIELD_NODE_ID:
//       await handleStatusChanged(itemNodeId, context);
//       break;
//     default:
//       break;
//   }
// }

// async function handleStatusChanged(itemNodeId: string, context: GitHubOperationsContext) {
//   const projectV2Item = await GraphQLUtil.getProjectV2ItemFieldValue(itemNodeId, 'Status', context);
//   const fieldValue = <ProjectV2ItemFieldSingleSelectValue>projectV2Item.fieldValueByName!;
//   const issue = <Issue>projectV2Item.content!;

//   switch (fieldValue.name) {
//     case 'Done':
//       await handleStatusDone(issue, context);
//       break;
//     default:
//       break;
//   }
// }

// async function handleStatusDone(issue: Issue, context: GitHubOperationsContext) {
//   const query = await GraphQLUtil.loadQuery('updateIssue');
//   const input: UpdateIssueInput = {
//     id: issue.id,
//     state: 'CLOSED',
//   };

//   await context.octokit.graphql(query, { input });
// }
