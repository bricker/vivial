import { TRAFFIC_SOURCE_COOKIE_NAME, deleteCookie, getAllEaveAccountCookies } from "../cookies";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

const signOutRegex = new RegExp(/(sign out)|(logout)/i);

export async function logoutEventHandler(event: MouseEvent) {
  if (event.target) {
    // TODO: drill deeper??
    const targetElement = castEventTargetToHtmlElement(event.target);
    const nodeName = targetElement?.nodeName.toUpperCase();

    // delete auth and traffic cookies on signout button click
    if ((nodeName === "A" || nodeName === "BUTTON") && (targetElement?.innerText ?? "").search(signOutRegex)) {
      deleteCookie({ name: TRAFFIC_SOURCE_COOKIE_NAME });
      for (const [cookieName, _] of getAllEaveAccountCookies()) {
        deleteCookie({ name: cookieName });
      }
    }
  }
}
