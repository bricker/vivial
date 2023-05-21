import { CommentedIssueEventPayload, ContentType } from './types.js';
import { addComment } from './lib/jira-api.js';
// import coreApiClient, { SubscriptionSource, SubscriptionSourceEvent, SubscriptionSourcePlatform } from './lib/core-api.js';

export const run = async (payload: CommentedIssueEventPayload) => {
  console.debug(payload.eventType);
  // console.debug(JSON.stringify(payload, undefined, 2));

  return;
  // FIXME: Hardcoded ID.
  if (payload.comment.author.accountId === '6406455093cf2599462fbd53') {
    return;
  }

  // const subscriptionSource: SubscriptionSource = {
  //   platform: SubscriptionSourcePlatform.jira,
  //   event: SubscriptionSourceEvent.jira_issue_comment,
  //   id: `P${payload.issue.fields.project!.id}#I${payload.issue.id}`,
  // };

  // await coreApiClient.getOrCreateSubscription(subscriptionSource);

  await addComment(payload.issue, [
    {
      type: 'paragraph',
      content: [
        {
          type: ContentType.text,
          text: "I haven't been taught how to respond to requests in Jira yet.",
        },
      ],
    },
  ]);

  // const upsertDocumentResponse = await coreApiClient.upsertDocument(document, subscriptionSource);

  // await coreApiClient.getOrCreateSubscription({
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
};
