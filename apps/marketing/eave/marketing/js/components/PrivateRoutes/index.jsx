import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';

import useUser from '../../hooks/useUser';

function PrivateRoutes() {
  const { userState } = useUser();
  const { authenticated } = userState;

  return (
    authenticated ? <Outlet /> : <Navigate to="/" />
  );
}

export default PrivateRoutes;
