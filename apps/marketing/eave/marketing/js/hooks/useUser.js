// @ts-check
import { useContext } from "react";
import { useCookies } from "react-cookie";
import { AppContext } from "../context/Provider.js";
import { isHTTPError, isUnauthorized, logUserOut } from "../util/http-util.js";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars

const _EAVE_LOGIN_STATE_HINT_COOKIE_NAME = "ev_login_state_hint";

/** @returns {{user: Types.DashboardUser, isLoginHintSet: boolean, getUserAccount: () => Promise<void>}} */
const useUser = () => {
  const { userCtx } = useContext(AppContext);
  const [cookies] = useCookies([_EAVE_LOGIN_STATE_HINT_COOKIE_NAME]);

  /** @type {[Types.DashboardUser, (f: (prev: Types.DashboardUser) => Types.DashboardUser) => void]} */
  const [user, setUser] = userCtx;

  const isLoginHintSet = cookies[_EAVE_LOGIN_STATE_HINT_COOKIE_NAME] === "1";

  /**
   * Asynchronously retrieves the user's account information from the server.
   * It updates the user state before, during, and after the fetch request.
   * - Before the request, it sets `accountIsLoading` to true and `accountIsErroring` to false.
   * - If the request is successful, it updates the `account` with the received data.
   * - If the request fails, it sets `accountIsErroring` to true.
   * - After the request (whether it succeeded or failed), it sets `accountIsLoading` to false.
   */
  async function getUserAccount() {
    setUser((prev) => ({
      ...prev,
      accountIsLoading: true,
      accountIsErroring: false,
    }));

    fetch("/dashboard/me", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp.json().then((data) => {
          setUser((prev) => ({ ...prev, account: data.account }));
        });
      })
      .catch(() => {
        setUser((prev) => ({ ...prev, accountIsErroring: true }));
      })
      .finally(() => {
        setUser((prev) => ({ ...prev, accountIsLoading: false }));
      });
  }

  return {
    user,
    isLoginHintSet,
    getUserAccount,
  };
};

export default useUser;
