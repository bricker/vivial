import { isHTTPError, isUnauthorized, logUserOut } from "$eave-dashboard/js/util/http-util";
import { useState } from "react";
import { eaveOrigin, eaveWindow } from "../types";

export interface AuthedUserHook {
  validateUserAuth: () => void;
  userIsAuthed: boolean;
}

const useAuth = (): AuthedUserHook => {
  const [userIsAuthed, setUserIsAuthed] = useState(false);

  function validateUserAuth() {
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/account/query`, {
      method: "POST",
      headers: {
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          setUserIsAuthed(false);
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }

        setUserIsAuthed(true);
      })
      .catch((e) => {
        console.error(e);
      });
  }

  return {
    validateUserAuth,
    userIsAuthed,
  };
};

export default useAuth;
