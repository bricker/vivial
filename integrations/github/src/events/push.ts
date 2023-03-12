import Bluebird from 'bluebird';
import { PushEvent } from '@octokit/webhooks-types';
import { Query, Scalars, Commit, Blob, TreeEntry, Repository } from '@octokit/graphql-schema';
import { GitHubOperationsContext } from '../types';
import coreApiClient, { SubscriptionSource, SubscriptionSourceEvent, EaveDocument } from '../lib/core-api.js';
import openai, { OpenAIModel } from '../lib/openai.js';
import * as GraphQLUtil from '../lib/graphql-util.js';
import appSettings from '../settings.js';

// eslint-disable-next-line operator-linebreak
const PROMPT_PREFIX =
  'You are Eave, an AI documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

export default async function handler(event: PushEvent, context: GitHubOperationsContext) {
  console.info('Processing push', event, context);

  await Bluebird.all(event.commits.map(async (eventCommit) => {
    const modifiedFiles = Array.from(new Set([...eventCommit.added, ...eventCommit.removed, ...eventCommit.modified]));

    await Bluebird.all(modifiedFiles.map(async (eventCommitTouchedFilename) => {
      const fileId = Buffer.from(eventCommitTouchedFilename).toString('base64');
      // TODO: Move this eventId algorithm into a shared location
      const eventId = [
        `${event.repository.node_id}`,
        `${fileId}`,
      ].join('#');

      const subscriptionSource: SubscriptionSource = {
        platform: 'github',
        event: SubscriptionSourceEvent.github_file_change,
        id: eventId,
      };

      const subscription = await coreApiClient.getSubscription(subscriptionSource);
      if (subscription === null) { return; }
      const query = await GraphQLUtil.loadQuery('getFileContents');

      const variables: {
        repoOwner: Scalars['String'],
        repoName: Scalars['String'],
        commitOid: Scalars['String'],
        filePath: Scalars['String']
      } = {
        repoOwner: event.repository.owner.name!,
        repoName: event.repository.name,
        commitOid: eventCommit.id, // FIXME: Is oid and id the same here?
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
        `${PROMPT_PREFIX}\n\n`
        + `${fileContents}\n\n`
        + `${codeDescriptionString}. `
        + 'Explain what the above code does: ';

      const openaiResponse = await openai.createCompletion({
        prompt,
        model: OpenAIModel.davinciCode,
        max_tokens: 500,
      });

      const document: EaveDocument = {
        title: `Description of code in ${repositoryName} ${filePath}`,
        content: openaiResponse,
      };

      const upsertDocumentResponse = await coreApiClient.upsertDocument(document, subscriptionSource);
      console.log(upsertDocumentResponse);
    }));
  }));
}
