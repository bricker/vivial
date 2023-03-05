import Bluebird from 'bluebird';
import { PushEvent } from '@octokit/webhooks-types';
import { Query, Scalars, Commit, Blob, TreeEntry, Repository } from '@octokit/graphql-schema';
import { GitHubOperationsContext } from '../types';
import coreApiClient, { SubscriptionSource, SubscriptionSourceEvent, EaveDocument } from '../lib/core-api';
import openai, { OpenAIModel } from '../lib/openai';
import * as GraphQLUtil from '../lib/graphql-util';
import appSettings from '../settings';

// eslint-disable-next-line operator-linebreak
const PROMPT_PREFIX =
  'You are Eave, an AI documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

export default async function handler(event: PushEvent, context: GitHubOperationsContext) {
  console.info('Processing push', event, context);

  await Bluebird.all(event.commits.map(async (commit) => {
    const modifiedFiles = Array.from(new Set([...commit.added, ...commit.removed, ...commit.modified]));

    await Bluebird.all(modifiedFiles.map(async (filePath) => {
      const eventId = [
        `R${event.repository.id}`,
        `F${modifiedFile}`,
      ].join('#');

      const subscriptionSource: SubscriptionSource = {
        event: SubscriptionSourceEvent.github_file_change,
        id: eventId,
      };

      const subscription = await coreApiClient.getSubscription(subscriptionSource);
      if (subscription === null) { return; }
      const query = await GraphQLUtil.loadQuery('getFileContents');

      const variables: { nodeId: Scalars['ID'], filePath: Scalars['String'] } = {
        nodeId: commit.id,
        filePath,
      };

      const response = await context.octokit.graphql<{ node: Query['node'] }>(query, variables);
      const commit = <Commit | undefined>response.node;
      if (commit === undefined) { return; }

      const repository = <Repository | undefined>commit.repository;
      if (repository === undefined) { return; }

      const file = <TreeEntry | undefined>commit.file;
      if (file === undefined) { return; }

      const blob = <Blob | undefined>file.object;
      if (blob === undefined) { return; }

      const fileContents = blob.text;
      if (fileContents === undefined) { return; }

      const codeDescription = [];

      const languageName = file.language?.name;
      if (languageName !== undefined) {
        codeDescription.push(`written in ${languageName}`);
      }

      const filePath = file.path;
      if (filePath !== undefined) {
        codeDescription.push(`in a file called "${filePath}"`);
      }

      const repositoryName = repository.name;
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

      const addlHeaders: {[key: string]: string} = {};

      if (appSettings.eaveDemoMode) {
        addlHeaders['eave-demo-mock-id'] = 'demo-doc-arch-02';
      }

      await coreApiClient.upsertDocument(document, subscriptionSource, addlHeaders);
    }));
  }));
}
