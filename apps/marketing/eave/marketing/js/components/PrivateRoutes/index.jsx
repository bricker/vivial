import React from "react";
import { Navigate, Outlet } from "react-router-dom";

import useUser from "../../hooks/useUser";

function PrivateRoutes() {
  const { isLoginHintSet } = useUser();
  return isLoginHintSet ? <Outlet /> : <Navigate to="/" />;
}

export default PrivateRoutes;
