import { eaveState } from "../state";
import { CurrentPageProperties } from "../types";

export function getCurrentPageProperties(): CurrentPageProperties {
  return {
    url: window.location.href,
    title: document.title,
    pageview_id: eaveState.pageViewId,
  };
}
