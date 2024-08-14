import { TRAFFIC_SOURCE_COOKIE_NAME, deleteCookie, getAllEaveAccountCookies } from "../cookies";
import { getClickableParentElement } from "../util/dom-helpers";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

const signOutRegex = new RegExp(/(sign ?out)|(log ?(out|off))/i);

export async function logoutEventHandler(event: MouseEvent) {
  if (event.target) {
    const targetElement = getClickableParentElement(castEventTargetToHtmlElement(event.target));

    // delete auth and traffic cookies on signout button click
    const targetContainsSignoutText = (targetElement?.innerText ?? "").search(signOutRegex) >= 0;
    if (targetElement && targetContainsSignoutText) {
      deleteCookie({ name: TRAFFIC_SOURCE_COOKIE_NAME });
      for (const [cookieName, _] of getAllEaveAccountCookies()) {
        deleteCookie({ name: cookieName });
      }
    }
  }
}
