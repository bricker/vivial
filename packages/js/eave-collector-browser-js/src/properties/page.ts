import { eaveState } from "../state";
import { PageProperties, StringMap } from "../types";

export function getPageProperties(): PageProperties {
  const currentPageUrl = new URL(window.location.href);
  const current_query_params = Array.from(currentPageUrl.searchParams.entries());

  return {
    current_url: currentPageUrl.toString(),
    current_title: document.title,
    pageview_id: eaveState.pageViewId,
    current_query_params,
  };
}
