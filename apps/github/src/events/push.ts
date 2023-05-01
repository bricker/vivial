import Bluebird from 'bluebird';
import { PushEvent } from '@octokit/webhooks-types';
import { Query, Scalars, Commit, Blob, TreeEntry, Repository } from '@octokit/graphql-schema';
import * as openai from '@eave-fyi/eave-stdlib-ts/src/openai';
import * as eaveCoreApiClient from '@eave-fyi/eave-stdlib-ts/src/core-api/client';
import * as eaveOps from '@eave-fyi/eave-stdlib-ts/src/core-api/operations';
import * as eaveEnums from '@eave-fyi/eave-stdlib-ts/src/core-api/enums';
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
      const branchName = event.ref.replace('refs/heads/', '');
      // TODO: Move this eventId algorithm into a shared location
      const eventId = [
        `${event.repository.node_id}`,
        `${branchName}/${eventCommitTouchedFilename}`,
      ].join('#');

      // fetch eave team id required for core_api requests
      const installationId = event.installation!.id;
      const teamResponse = await eaveCoreApiClient.getGithubInstallation({
        github_installation: {
          github_install_id: `${installationId}`,
        },
      });
      if (teamResponse === null) { return; }
      const eaveTeamId = teamResponse.team.id;

      // check if we are subscribed to this file
      const subscriptionResponse = await eaveCoreApiClient.getSubscription(eaveTeamId, {
        subscription: {
          source: {
            platform: eaveEnums.SubscriptionSourcePlatform.github,
            event: eaveEnums.SubscriptionSourceEvent.github_file_change,
            id: eventId,
          },
        },
      });
      if (subscriptionResponse === null) { return; }

      // get file content so we can document the changes
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

      // build a description of the file
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

      // have AI explain the code
      // TODO: implement rolling content summary
      // FIXME: Add this eslint exception to eslint config
      // eslint-disable-next-line operator-linebreak
      const prompt =
        `${openai.PROMPT_PREFIX}\n\n`
        + `${fileContents}\n\n`
        + `${codeDescriptionString}. `
        + 'Explain what the above code does: ';

      // FIXME: using gpt3.5 for now since openai node module docs for CreateChatCompletionRequest
      // currently says it only supports gtp3.5 turbo models. not sure if thats actually true tho
      const openaiResponse = await openai.createChatCompletion({
        messages: [{ role: 'user', content: prompt }],
        model: openai.OpenAIModel.GPT_35_TURBO,
        max_tokens: openai.MAX_TOKENS[openai.OpenAIModel.GPT_35_TURBO],
      });

      const document: eaveOps.DocumentInput = {
        title: `Description of code in ${repositoryName} ${filePath}`,
        content: openaiResponse,
      };

      // TODO: this should be updating existing document, not completely replacing
      const upsertDocumentResponse = await eaveCoreApiClient.upsertDocument(
        eaveTeamId,
        {
          document,
          subscription: subscriptionResponse.subscription,
        },
      );

      console.log(upsertDocumentResponse);
    }));
  }));
}
