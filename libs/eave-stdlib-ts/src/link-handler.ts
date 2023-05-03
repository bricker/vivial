import Bluebird from 'bluebird';
import * as eaveClient from './core-api/client';
import { LinkType, SubscriptionSourceEvent, SubscriptionSourcePlatform } from './core-api/enums';
import { Pair } from './types';
import { ApiClientBase } from './third-party-api-clients/base';
import { GithubClient } from './third-party-api-clients/github';
import { createClient, LinkContext } from './third-party-api-clients/util';


// mapping from link type to regex for matching raw links against
const SUPPORTED_LINKS: { [linkType: string]: Array<RegExp> } = {
  [LinkType.github]: [
    /github\.com/,
    /github\..+\.com/,
  ],
}

export function filterSupportedLinks(urls: Array<string>): Array<Pair<string, LinkType>> {
  const supportedLinks: Array<Pair<string, LinkType>> = [];
  urls.forEach(link => {
    const linkType = getLinkType(link);
    if (linkType !== null) {
      supportedLinks.push({ first: link, second: linkType });
    }
  });
  return supportedLinks;
}

/**
 * Given a list of urls, returns mapping to content found at each link. Order is preserved.
 *
 * If an error is encountered while attempting to access the info at a link, the value at
 * the position of the link in the returned list is None.
 */
export async function mapUrlContent(eaveTeamId: string, urls: Array<Pair<string, LinkType>>): Promise<Array<string | null>> {
  const contexts = await buildLinkContexts(eaveTeamId, urls);

  // string key is a LinkType case, but ts won't let me define it that way
  const clients: { [key: string]: ApiClientBase; } = {};
  const contentResponses = await Bluebird.map(contexts, async (linkContext) => {
    if (!(linkContext.type in clients)) {
      clients[linkContext.type] = createClient(linkContext);
    }
    switch (linkContext.type) {
      case LinkType.github:
        return clients[linkContext.type]!.getFileContent(linkContext.url);
    }
  });

  return contentResponses;
}


/** 
 * Create Eave Subscriptions to watch for changes in all of the URL resources in `urls`
 * 
 * @param eaveTeamId -- TeamOrm ID to create the subscription for
 * @param urls -- links paired with their platform type [(url, url platform)]
 */
export async function subscribe(eaveTeamId: string, urls: Array<Pair<string, LinkType>>): Promise<void> {
  const contexts = await buildLinkContexts(eaveTeamId, urls);

  // string key is a LinkType case, but ts won't let me define it that way
  const clients: { [key: string]: ApiClientBase; } = {};
  contexts.forEach(linkContext => {
    if (!(linkContext.type in clients)) {
      clients[linkContext.type] = createClient(linkContext);
    }

    // launch async task
    createSubscription(clients[linkContext.type]!, linkContext.url, linkContext.type, eaveTeamId);
  });
}

// smelly conversion from string to enum case to make ts happy
function stringToLinkType(value: string): LinkType | null {
  switch (value) {
    case 'github': return LinkType.github;
  }
  return null;
}

/** 
 * Given a link, determine if we support parsing the content from that link.
 * @returns link type if supported, otherwise None
 */
function getLinkType(link: string): LinkType | null {
  const domain = (new URL(link)).hostname;
  let returnValue = null;
  Object.keys(SUPPORTED_LINKS).forEach(linkType => {
    const patterns = SUPPORTED_LINKS[linkType]!;
    patterns.forEach(pattern => {
      if (domain.match(pattern)) {
        returnValue = stringToLinkType(linkType);
      }
    });
  });
  return returnValue;
}

/** 
 * Given a collection of links and an Eave TeamOrm ID, return the data
 * required to authenticate with the 3rd party API for each link.
 * If the Eave Team is not integrated with platform the link is from,
 * that link is filtered out of the returned list, as the Team account
 * has not explicitly given us permission to attempt to read data from
 * those links.
 * 
 * @param eaveTeamId -- ID of the Eave TeamOrm to fetch platform integrations from
 * @param links -- list of links to build API client auth data for
 */
async function buildLinkContexts(eaveTeamId: string, links: Array<Pair<string, LinkType>>): Promise<Array<LinkContext>> {
  // fetch from core_api what sources are connected, and the auth data required to query their API
  const teamResponse = await eaveClient.getTeam(eaveTeamId)

  const apiClientAuthData: { [linkType: string]: string; } = {};
  for (const supportedTypeString in LinkType) {
    const supporetdType = stringToLinkType(supportedTypeString);
    switch (supporetdType) {
      case LinkType.github:
        const ghIntegration = teamResponse.integrations.github;
        if (ghIntegration !== undefined) {
          apiClientAuthData[LinkType.github] = ghIntegration.github_install_id;
        }
    }
  }

  // filter URLs to platforms the user has linked their eave account to
  const accessibleLinks: Array<LinkContext> = [];
  links.forEach(pair => {
    const { first: link, second: linkType } = pair;
    if (linkType in apiClientAuthData) {
      accessibleLinks.push({
        url: link,
        type: linkType,
        authData: apiClientAuthData[linkType],
      });
    }
  });
  return accessibleLinks;
}


/**
 * Insert a subcription to watch the resource at `url` into the Eave database.
 * 
 * @param untyped_client -- API client corresponding to `linkType` for fetching data to build subscription with
 * @param url -- URL resource to create a subscription for watching
 * @param linkType -- resource platform to subscribe on
 * @param eaveTeamId -- ID of team to associate subscription with
 */
async function createSubscription(baseClient: ApiClientBase, url: string, linkType: LinkType, eaveTeamId: string): Promise<void> {
  let sourceId: string | null = null;
  let platform: SubscriptionSourcePlatform | null = null;
  let event: SubscriptionSourceEvent | null = null;

  // populate required subscription data based on link type
  switch (linkType) {
    case LinkType.github:
      const client = <GithubClient>baseClient;
      // fetch unique info about repo to build subscription source ID
      const repoInfo = await client.getRepo(url);
      const pathChunks = url.split(`${repoInfo.full_name}/blob/`);
      // we need the 2nd element, which is branch name + resource path
      if (pathChunks.length < 2) { return; }
      const blobPath = pathChunks[1];
      sourceId = `${repoInfo.node_id}#${blobPath}`;
      platform = SubscriptionSourcePlatform.github;
      event = SubscriptionSourceEvent.github_file_change;
  }

  if (sourceId !== null && platform !== null && event !== null) {
    await eaveClient.createSubscription(eaveTeamId, {
      subscription: {
        source: {
          platform,
          event,
          id: sourceId,
        }
      }
    })
  }
}
