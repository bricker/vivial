import { TRAFFIC_SOURCE_COOKIE_NAME, deleteCookie, getAllEaveAccountCookies } from "../cookies";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

const signOutRegex = new RegExp(/(sign out)|(logout)/i);

export async function logoutEventHandler(event: MouseEvent) {
  console.log("handling logout?");
  if (event.target) {
    // TODO: drill deeper?? search for wrapping button around clicked elem?
    const targetElement = castEventTargetToHtmlElement(event.target);
    const nodeName = targetElement?.nodeName.toUpperCase();
    console.log("got clieked element", nodeName, targetElement);

    // delete auth and traffic cookies on signout button click
    const targetContainsSignoutText = !(targetElement?.innerText ?? "").search(signOutRegex);
    if ((nodeName === "A" || nodeName === "BUTTON") && targetContainsSignoutText) {
      console.log("deleting cookeis!");
      deleteCookie({ name: TRAFFIC_SOURCE_COOKIE_NAME });
      for (const [cookieName, _] of getAllEaveAccountCookies()) {
        deleteCookie({ name: cookieName });
      }
    }
  }
}
