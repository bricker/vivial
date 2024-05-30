import React, { useState } from "react";
import styles from "./CookieBanner.module.css";
import { COOKIE_PREFIX, deleteAllCookies, getCookie, setCookie } from "./cookies";

const consentCookieName = `${COOKIE_PREFIX}consent`;
const consentCookieMaxAge = 2592000;

const consentChoices = {
  ACCEPTED: "1",
  REJECTED: "0",
};

const CookieConsentBanner = () => {
  const consentCookieValue = getCookie(consentCookieName);
  const [consentChoice, setConsentChoice] = useState(consentCookieValue);

  const handleAccept = () => {
    const choiceValue = consentChoices.ACCEPTED;
    setConsentChoice(choiceValue);

    // This is for the Todoapp's record. Eave manages its own consent cookies.
    setCookie({
      name: consentCookieName,
      value: choiceValue,
      maxAge: consentCookieMaxAge,
    });

    // @ts-expect-error: window.eave is defined by the Eave collector library
    window.eave?.enableAll();
  };

  const handleReject = () => {
    const choiceValue = consentChoices.REJECTED;
    setConsentChoice(choiceValue);

    // This is for the Todoapp's record. Eave manages its own consent cookies.
    deleteAllCookies();
    setCookie({
      name: consentCookieName,
      value: choiceValue,
      maxAge: consentCookieMaxAge,
    });

    // @ts-expect-error: window.eave is defined by the Eave collector library
    window.eave?.disableAll();
  };

  if (consentChoice !== null) {
    // If the user has already made a choice, don't show the banner.
    return null;
  }

  return (
    <div className={styles.cookieBanner}>
      <p>This website uses cookies to ensure you get the best experience.</p>
      <button onClick={handleAccept}>Accept</button>
      <button onClick={handleReject}>Reject</button>
    </div>
  );
};

export default CookieConsentBanner;
