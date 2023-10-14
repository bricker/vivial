import { useContext } from "react";
import { AppContext } from "../context/Provider.js";
import { isHTTPError } from "../util/http-util.js";

const useUser = () => {
  const { userCtx } = useContext(AppContext);
  const [user, setUser] = userCtx;

  /**
   * Asynchronously checks the user's authentication status by making a fetch request to "/authcheck".
   * If the response indicates an HTTP error, it throws the response.
   * If the response is successful, it updates the user's authentication status in the state.
   * If there's an error in the process, it sets the 'authIsErroring' state to true.
   */
  async function checkUserAuth() {
    fetch("/authcheck")
      .then((resp) => {
        if (isHTTPError(resp)) {
          throw resp;
        }
        resp.json().then((data) => {
          setUser((prev) => ({ ...prev, isAuthenticated: data.authenticated }));
        });
      })
      .catch(() => {
        setUser((prev) => ({ ...prev, authIsErroring: true }));
      });
  }

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
    fetch("/dashboard/me", { method: "POST" })
      .then((resp) => {
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

  /**
   * Asynchronously logs the user out by redirecting to the logout page.
   */
  async function logUserOut() {
    window.location.assign("/dashboard/logout");
  }

  return {
    user,
    checkUserAuth,
    getUserAccount,
    logUserOut,
  };
};

export default useUser;
