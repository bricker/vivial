import { useContext } from "react";
import { AppContext } from "../context/Provider.js";
import { isHTTPError } from "../util/http-util.js";

const useUser = () => {
  const { userCtx } = useContext(AppContext);
  const [user, setUser] = userCtx;

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
