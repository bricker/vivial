import { LinkType } from "./core-api/enums.js";
import { Subscription } from "./core-api/models/subscriptions.js";
import { CreateGithubResourceSubscriptionOperation } from "./github-api/operations/create-subscription.js";
import { GetGithubUrlContentOperation } from "./github-api/operations/get-content.js";
import { eaveLogger } from "./logging.js";
import { RequestArgsTeamId } from "./requests.js";
import { Pair } from "./types.js";

// mapping from link type to regex for matching raw links against
const SUPPORTED_LINKS: { [linkType: string]: Array<RegExp> } = {
  [LinkType.github]: [/github\.com/, /github\..+\.com/],
};

export function filterSupportedLinks(urls: Array<string>): Array<Pair<string, LinkType>> {
  const supportedLinks: Array<Pair<string, LinkType>> = [];
  urls.forEach((link) => {
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
export async function mapUrlContent({ origin, teamId, urls, ctx }: RequestArgsTeamId & { urls: Array<Pair<string, LinkType>> }): Promise<Array<string | null>> {
  const contentResponses = await Promise.all(
    urls.map(async (linkContext: Pair<string, LinkType>) => {
      const { first: url, second: type } = linkContext;

      switch (type) {
        case LinkType.github: {
          const contentResponse = await GetGithubUrlContentOperation.perform({
            ctx,
            origin,
            teamId,
            input: {
              url,
            },
          });
          return contentResponse.content;
        }
        default:
          eaveLogger.warning(`unsupported link type: ${type}`, ctx);
          return null;
      }
    }),
  );

  return contentResponses;
}

/**
 * Create Eave Subscriptions to watch for changes in all of the URL resources in `urls`
 *
 * @param eaveTeamId -- TeamOrm ID to create the subscription for
 * @param urls -- links paired with their platform type [(url, url platform)]
 */
export async function subscribeToFileChanges({ origin, teamId, urls, ctx }: RequestArgsTeamId & { urls: Array<Pair<string, LinkType>> }): Promise<Array<Subscription>> {
  // string key is a LinkType case, but ts won't let me define it that way
  const subscriptions: Array<Subscription> = [];
  urls.forEach(async (linkContext) => {
    const { first: url, second: linkType } = linkContext;
    const maybeSubscription = await createSubscription({ origin, teamId, url, linkType, ctx });

    if (maybeSubscription !== null) {
      subscriptions.push(maybeSubscription);
    }
  });
  return subscriptions;
}

// smelly conversion from string to enum case to make ts happy
function stringToLinkType(value: string): LinkType | null {
  switch (value) {
    case "github":
      return LinkType.github;
    default:
      return null;
  }
}

/**
 * Given a link, determine if we support parsing the content from that link.
 * @returns link type if supported, otherwise None
 */
function getLinkType(link: string): LinkType | null {
  const domain = new URL(link).hostname;
  let returnValue = null;
  Object.keys(SUPPORTED_LINKS).forEach((linkType) => {
    const patterns = SUPPORTED_LINKS[linkType]!;
    patterns.forEach((pattern) => {
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
async function createSubscription({ origin, teamId, url, linkType, ctx }: RequestArgsTeamId & { url: string; linkType: LinkType }): Promise<Subscription | null> {
  switch (linkType) {
    case LinkType.github: {
      const subscriptionResponse = await CreateGithubResourceSubscriptionOperation.perform({
        ctx,
        origin,
        teamId,
        input: {
          url,
        },
      });
      return subscriptionResponse.subscription;
    }
    default:
      eaveLogger.warning(`unsupported link type: ${linkType}`, ctx);
      return null;
  }
}
