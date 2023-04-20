import Bluebird from 'bluebird';
import { PushEvent } from '@octokit/webhooks-types';
import { Query, Scalars, Commit, Blob, TreeEntry, Repository } from '@octokit/graphql-schema';
import * as openai from '@eave-fyi/eave-stdlib-ts/src/openai';
import * as eaveCoreApiClient from '@eave-fyi/eave-stdlib-ts/src/core-api/client';
import * as eaveOps from '@eave-fyi/eave-stdlib-ts/src/core-api/operations';
import * as eaveModels from '@eave-fyi/eave-stdlib-ts/src/core-api/models';
import { GitHubOperationsContext } from '../types';
import * as GraphQLUtil from '../lib/graphql-util.js';

export default async function handler(event: PushEvent, context: GitHubOperationsContext) {
  console.info('Processing push', event, context);

  // TODO: This event only contains a maximum of 20 commits. Additional commits need to be fetched from the API.
  // Also, this event is not triggered when more than 3 tags are pushed.
  // https://docs.github.com/webhooks-and-events/webhooks/webhook-events-and-payloads#push
  await Bluebird.all(event.commits.map(async (eventCommit) => {
    const modifiedFiles = Array.from(new Set([...eventCommit.added, ...eventCommit.removed, ...eventCommit.modified]));

    await Bluebird.all(modifiedFiles.map(async (eventCommitTouchedFilename) => {
      const fileId = Buffer.from(eventCommitTouchedFilename).toString('base64');
      // TODO: Move this eventId algorithm into a shared location
      const eventId = [
        `${event.repository.node_id}`,
        `${fileId}`,
      ].join('#');

      // FIXME: Hardcoded team ID
      const subscriptionResponse = await eaveCoreApiClient.getSubscription('3345217c-fb27-4422-a3fc-c404b49aff8c', {
        subscription: {
          source: {
            platform: eaveModels.SubscriptionSourcePlatform.github,
            event: eaveModels.SubscriptionSourceEvent.github_file_change,
            id: eventId,
          },
        },
      });

      if (subscriptionResponse === null) { return; }
      const query = await GraphQLUtil.loadQuery('getFileContents');

      const variables: {
        repoOwner: Scalars['String'],
        repoName: Scalars['String'],
        commitOid: Scalars['String'],
        filePath: Scalars['String']
      } = {
        repoOwner: event.repository.owner.name!,
        repoName: event.repository.name,
        commitOid: eventCommit.id,
        filePath: eventCommitTouchedFilename,
      };

      const fileContentsResponse = await context.octokit.graphql<{ repository: Query['repository'] }>(query, variables);
      const fileContentsRepository = <Repository>fileContentsResponse.repository!;
      const fileContentsCommit = <Commit>fileContentsRepository.object!;
      const fileContentsTreeEntry = <TreeEntry>fileContentsCommit.file!;
      const fileContentsBlob = <Blob>fileContentsTreeEntry.object!;
      const fileContents = fileContentsBlob.text!;

      const codeDescription = [];

      const languageName = fileContentsTreeEntry.language?.name;
      if (languageName !== undefined) {
        codeDescription.push(`written in ${languageName}`);
      }

      const filePath = fileContentsTreeEntry.path;
      if (filePath !== undefined) {
        codeDescription.push(`in a file called "${filePath}"`);
      }

      const repositoryName = fileContentsRepository.name;
      codeDescription.push(`in a Github repository called "${repositoryName}"`);

      const codeDescriptionString = codeDescription.length > 0
        ? `# The above code is ${codeDescription.join(', ')}`
        : '';

      // FIXME: Add this eslint exception to eslint config
      // eslint-disable-next-line operator-linebreak
      const prompt =
        `${openai.PROMPT_PREFIX}\n\n`
        + `${fileContents}\n\n`
        + `${codeDescriptionString}. `
        + 'Explain what the above code does: ';

      const openaiResponse = await openai.createCompletion({
        prompt,
        model: openai.OpenAIModel.davinciCode,
        max_tokens: 500,
      });

      const document: eaveOps.DocumentInput = {
        title: `Description of code in ${repositoryName} ${filePath}`,
        content: openaiResponse,
      };

      // FIXME: no hardcode id
      const upsertDocumentResponse = await eaveCoreApiClient.upsertDocument(
        '3345217c-fb27-4422-a3fc-c404b49aff8c',
        {
          document,
          subscription: subscriptionResponse.subscription,
        },
      );

      console.log(upsertDocumentResponse);
    }));
  }));
}
