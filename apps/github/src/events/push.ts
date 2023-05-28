import { PushEvent } from '@octokit/webhooks-types';
import { Query, Scalars, Commit, Blob, TreeEntry, Repository } from '@octokit/graphql-schema';
import * as openai from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import * as eaveCoreApiClient from '@eave-fyi/eave-stdlib-ts/src/core-api/client.js';
import * as eaveOps from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/operations.js';
import * as eaveEnums from '@eave-fyi/eave-stdlib-ts/src/core-api/enums.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { GitHubOperationsContext } from '../types.js';
import * as GraphQLUtil from '../lib/graphql-util.js';
import { appConfig } from '../config.js';

export default async function handler(event: PushEvent, context: GitHubOperationsContext) {
  eaveLogger.debug('Processing push', { event, context });

  // only handling branch push events for now; ignore tag pushes
  if (!event.ref.startsWith('refs/heads/')) {
    eaveLogger.debug(`Ignoring event with ref ${event.ref}`);
    return;
  }

  // TODO: This event only contains a maximum of 20 commits. Additional commits need to be fetched from the API.
  // Also, this event is not triggered when more than 3 tags are pushed.
  // https://docs.github.com/webhooks-and-events/webhooks/webhook-events-and-payloads#push
  await Promise.all(event.commits.map(async (eventCommit) => {
    const modifiedFiles = Array.from(new Set([...eventCommit.added, ...eventCommit.removed, ...eventCommit.modified]));

    await Promise.all(modifiedFiles.map(async (eventCommitTouchedFilename) => {
      const branchName = event.ref.replace('refs/heads/', '');
      // b64 encode since our chosen ID delimiter '#' is a valid character in file paths and branch names
      const resourceId = Buffer.from(`${branchName}/${eventCommitTouchedFilename}`).toString('base64');
      // TODO: Move this eventId algorithm into a shared location
      const eventId = [
        event.repository.node_id,
        resourceId,
      ].join('#');

      // fetch eave team id required for core_api requests
      const installationId = event.installation!.id;
      const teamResponse = await eaveCoreApiClient.getGithubInstallation({
        origin: appConfig.origin,
        input: {
          github_installation: {
            github_install_id: `${installationId}`,
          },
        },
      });
      const eaveTeamId = teamResponse.team.id;

      // check if we are subscribed to this file
      let subscriptionResponse: eaveOps.GetSubscriptionResponseBody | null = null;
      try {
        subscriptionResponse = await eaveCoreApiClient.getSubscription({
          origin: appConfig.origin,
          teamId: eaveTeamId,
          input: {
            subscription: {
              source: {
                platform: eaveEnums.SubscriptionSourcePlatform.github,
                event: eaveEnums.SubscriptionSourceEvent.github_file_change,
                id: eventId,
              },
            },
          },
        });
      } catch (error) {
        // TODO: only catch 404?
        eaveLogger.error(error);
        // return;
      }

      if (subscriptionResponse === null) {
        return;
      }

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

      // have AI explain the code change
      // TODO: implement rolling content summary
      // FIXME: Add this eslint exception to eslint config
      // eslint-disable-next-line operator-linebreak
      const prompt =
        `${fileContents}\n\n`
        + `${codeDescriptionString}. `
        + 'Explain what the above code does: ';

      // NOTE: According to the OpenAI docs, model gpt-3.5-turbo-0301 doesn't pay attention to the system messages,
      // but it seems it's specific to that model, and neither gpt-3.5-turbo or gpt-4 are affected, so watch out
      const openaiResponse = await openai.createChatCompletion({
        messages: [
          { role: 'system', content: openai.PROMPT_PREFIX },
          { role: 'user', content: prompt },
        ],
        model: openai.OpenAIModel.GPT4,
        max_tokens: openai.MAX_TOKENS[openai.OpenAIModel.GPT4],
      });

      const document: eaveOps.DocumentInput = {
        title: `Description of code in ${repositoryName} ${filePath}`,
        content: openaiResponse,
      };

      const upsertDocumentResponse = await eaveCoreApiClient.upsertDocument({
        origin: appConfig.origin,
        teamId: eaveTeamId,
        input: {
          document,
          subscriptions: [subscriptionResponse.subscription],
        },
      });

      eaveLogger.debug(upsertDocumentResponse);
    }));
  }));
}
