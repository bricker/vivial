import Bluebird from 'bluebird';
import * as githubClient from './github-api/client';
import { LinkType } from './core-api/enums';
import { Pair } from './types';
import { Subscription } from './core-api/models';


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
  const contentResponses = await Bluebird.map(urls, async (linkContext: Pair<string, LinkType>) => {
    const { first: url, second: type } = linkContext;

    switch (type) {
      case LinkType.github:
        const contentResponse = await githubClient.getFileContent(eaveTeamId, {
          url,
          eaveTeamId,
        });
        return contentResponse.content;
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
export async function subscribeToFileChanges(eaveTeamId: string, urls: Array<Pair<string, LinkType>>): Promise<Array<Subscription>> {
  // string key is a LinkType case, but ts won't let me define it that way
  const subscriptions: Array<Subscription> = [];
  urls.forEach(async (linkContext) => {
    const { first: url, second: type } = linkContext;
    const maybeSubscription = await createSubscription(url, type, eaveTeamId);

    if (maybeSubscription !== null) {
      subscriptions.push(maybeSubscription);
    }
  });
  return subscriptions;
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
 * Insert a subcription to watch the resource at `url` into the Eave database.
 * 
 * @param url -- URL resource to create a subscription for watching
 * @param linkType -- resource platform to subscribe on
 * @param eaveTeamId -- ID of team to associate subscription with
 */
async function createSubscription(url: string, linkType: LinkType, eaveTeamId: string): Promise<Subscription | null> {
  switch (linkType) {
    case LinkType.github:
      const subscriptionResponse = await githubClient.createSubscription(eaveTeamId, {
        url,
        eaveTeamId,
      });
      return subscriptionResponse.subscription;
  }

  return null;
}
