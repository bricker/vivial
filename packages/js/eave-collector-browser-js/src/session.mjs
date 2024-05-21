import { cookieManager } from "./cookies.mjs";
import { uuidv4 } from "./helpers.mjs";

const SESSION_ID_COOKIE_NAME = "session_id";
const VISITOR_ID_COOKIE_NAME = "visitor_id";

class SessionManager {
  constructor() {}

  /**
   * @returns {string | undefined}
   */
  getSessionId() {
    return cookieManager.getCookie(SESSION_ID_COOKIE_NAME);
  }

  /**
   * Resets the expiration of the session cookie, or sets a new
   * value if there was no existing session cookie.
   *
   * @noreturn
   */
  resetOrExtendSession() {
    const sessionId = this.getSessionId() || uuidv4();
    cookieManager.setCookie(
      SESSION_ID_COOKIE_NAME,
      sessionId,
      this.configSessionCookieTimeout,
      this.configCookiePath,
      this.configCookieDomain,
      this.configCookieIsSecure,
      this.configCookieSameSite,
    );
  }

  /**
   * Get visitor ID (from first party cookie)
   *
   * @returns {string | undefined} Visitor ID
   */
  getVisitorId() {
    return cookieManager.getCookie(VISITOR_ID_COOKIE_NAME);
  };

  /**
   * Set visitor ID if it hasnt yet been set.
   *
   * @noreturn
   */
  setVisitorId() {
    if (!this.getVisitorId()) {
      cookieManager.setCookie(VISITOR_ID_COOKIE_NAME, uuidv4());
    }
  }
}

export const sessionManager = new SessionManager();