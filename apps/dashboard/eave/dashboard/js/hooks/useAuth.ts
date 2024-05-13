import {
  isHTTPError,
  isUnauthorized,
  logUserOut,
} from "$eave-dashboard/js/util/http-util";
import { useState } from "react";

export interface AuthedUserHook {
  validateUserAuth: () => void;
  userIsAuthed: boolean;
}

const useAuth = (): AuthedUserHook => {
  const [userIsAuthed, setUserIsAuthed] = useState(false);

  function validateUserAuth() {
    fetch("/api/auth", {
      method: "GET",
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
      })
      .catch(() => {
        // TODO
      });
  }

  return {
    validateUserAuth,
    userIsAuthed,
  };
};

export default useAuth;
