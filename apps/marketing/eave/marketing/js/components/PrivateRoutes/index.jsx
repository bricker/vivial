import React, { useEffect } from 'react';
import { Outlet, Navigate } from 'react-router-dom';

import useUser from '../../hooks/useUser';

function PrivateRoutes() {
  const { userState, checkUserAuthState } = useUser();
  const { authenticated } = userState;

  useEffect(() => {
    checkUserAuthState();
  }, [authenticated]);

  if (authenticated === null) {
    return null;
  }

  return (
    authenticated ? <Outlet /> : <Navigate to="/" />
  );
}

export default PrivateRoutes;
