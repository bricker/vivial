// import { IssuesLabeledEvent } from '@octokit/webhooks-types';
// import { ProjectV2Item, ProjectV2SingleSelectField, UpdateProjectV2ItemFieldValueInput } from '@octokit/graphql-schema';
// import * as GraphQLUtil from '../graphql-util';
// import { GitHubOperationsContext } from '../types';

// export default async function handler(event: IssuesLabeledEvent, context: GitHubOperationsContext) {
//   console.info('Processing issues.labeled', event);

//   const issue = await GraphQLUtil.getIssueByNodeId(event.issue.node_id, context);

//   if (issue.projectItems.totalCount === 0) {
//     console.warn('Issue has no associated ProjectV2Item.', issue.id);
//     return;
//   }

//   const item = <ProjectV2Item>issue.projectItems!.nodes![0];

//   switch (event.label!.name) {
//     case 'Epic':
//       await updateIssueType(item, 'Epic', context);
//       break;
//     case 'Bug':
//       await updateIssueType(item, 'Bug', context);
//       break;
//     default:
//       break;
//   }
// }

// async function updateIssueType(item: ProjectV2Item, issueType: string, context: GitHubOperationsContext) {
//   const issueTypeField = <ProjectV2SingleSelectField>(await GraphQLUtil.getProjectV2Field('Issue Type', context));
//   const option = issueTypeField.options.find((it) => it.name === issueType)!;

//   const query = await GraphQLUtil.loadQuery('updateProjectV2ItemFieldValue');
//   const input: UpdateProjectV2ItemFieldValueInput = {
//     fieldId: issueTypeField.id,
//     itemId: item.id,
//     projectId: item.project.id,
//     value: {
//       singleSelectOptionId: option.id,
//     },
//   };

//   await context.octokit.graphql(query, { input });
// }
