import { TRAFFIC_SOURCE_COOKIE_NAME, deleteCookie, getAllEaveAccountCookies } from "../cookies";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

const signOutRegex = new RegExp(/(sign ?out)|(log ?(out|off))/i);

export async function logoutEventHandler(event: MouseEvent) {
  if (event.target) {
    // climb up DOM tree to find any wrapping anchor or button element
    let targetElement = castEventTargetToHtmlElement(event.target);
    let nodeName = targetElement?.nodeName.toUpperCase();
    while (targetElement && !(nodeName === "A" || nodeName === "BUTTON")) {
      targetElement = targetElement.parentElement;
      nodeName = targetElement?.nodeName.toUpperCase();
    }

    // delete auth and traffic cookies on signout button click
    const targetContainsSignoutText = (targetElement?.innerText ?? "").search(signOutRegex) >= 0;
    if ((nodeName === "A" || nodeName === "BUTTON") && targetContainsSignoutText) {
      deleteCookie({ name: TRAFFIC_SOURCE_COOKIE_NAME });
      for (const [cookieName, _] of getAllEaveAccountCookies()) {
        deleteCookie({ name: cookieName });
      }
    }
  }
}
