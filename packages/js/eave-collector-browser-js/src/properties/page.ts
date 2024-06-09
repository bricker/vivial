import { eaveState } from "../state";
import { CurrentPageProperties, ScalarMap } from "../types";

export function currentQueryParams(): ScalarMap<string> {
  const currentPageUrl = new URL(window.location.href);
  const queryParams: ScalarMap<string> = {};

  for (const [key, value] of currentPageUrl.searchParams) {
    queryParams[key] = value;
  }

  return queryParams;
}

export function getCurrentPageProperties(): CurrentPageProperties {
  const currentPageUrl = new URL(window.location.href);
  const query_params = currentQueryParams();

  // Remove potentially sensitive properties
  currentPageUrl.username = "";
  currentPageUrl.password = "";

  return {
    url: {
      // This is done instead of toString() to remove username
      raw: currentPageUrl.toString(),
      protocol: currentPageUrl.protocol.replace(":$", ""),
      domain: currentPageUrl.hostname,
      path: currentPageUrl.pathname,
      hash: currentPageUrl.hash,
      query_params,
    },
    title: document.title,
    pageview_id: eaveState.pageViewId,
  };
}
