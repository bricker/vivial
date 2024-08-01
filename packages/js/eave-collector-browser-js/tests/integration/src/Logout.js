import React, { useEffect } from "react";
import { useCookies } from "react-cookie";
import { Link } from "react-router-dom";
import { AUTH_COOKIE_NAME } from "./util/cookies";

const Logout = () => {
  // delete auth cookie
  const [cookies, setCookie, removeCookie] = useCookies([AUTH_COOKIE_NAME]);
  useEffect(() => {
    removeCookie(AUTH_COOKIE_NAME);
  }, []);
  return (
    <>
      <h1>You're logged out right now!</h1>
      <Link id="home" to="/">
        Go home?
      </Link>
    </>
  );
};

export default Logout;
