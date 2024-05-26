import { eaveState } from "../state.js";
import { PageProperties, StringMap } from "../types.js";

export function getPageProperties(): PageProperties {
  const currentPageUrl = new URL(window.location.href);
  const current_query_params: StringMap<string[]> = {};

  currentPageUrl.searchParams.forEach((key, value) => {
    current_query_params[key] ||= [];
    current_query_params[key]?.push(value);
  });

  return {
    current_url: currentPageUrl.toString(),
    current_title: document.title,
    pageview_id: eaveState.pageViewId,
    current_query_params,
  }
}