import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import { CommentedIssueEventPayload } from '../types';

export default async function jiraCommentedIssueEventHandler(event: CommentedIssueEventPayload) {
  eaveLogger.info('jiraCommentedIssue', event);
  // const subscriptionSource: SubscriptionSource = {
  //   platform: SubscriptionSourcePlatform.jira,
  //   event: SubscriptionSourceEvent.jira_issue_comment,
  //   id: `P${payload.issue.fields.project!.id}#I${payload.issue.id}`,
  // };

  // const upsertDocumentResponse = await coreApiClient.upsertDocument(appConfig.eaveOrigin, 'xxx', document, subscriptionSource);

  // await coreApiClient.createSubscription({
  //   platform: SubscriptionSourcePlatform.github,
  //   event: SubscriptionSourceEvent.github_file_change,
  //   // FIXME: Remove this hardcoded id and get the real github information
  //   id: 'R_kgDOJDutMQ#YXBwLnB5', // finny-credit-application-processor/app.py
  // }, upsertDocumentResponse.document_reference.id);

  // await addComment(payload.issue, [
  //   {
  //     type: 'paragraph',
  //     content: [
  //       {
  //         type: ContentType.text,
  //         text: "Here's the documentation you requested! ",
  //         marks: [
  //           {
  //             type: ContentType.link,
  //             attrs: {
  //               href: upsertDocumentResponse.document_reference.document_url,
  //               title: 'Finny Credit Application System Architecture',
  //             },
  //           },
  //         ],
  //       },
  //     ],
  //   },
  // ]);
}
