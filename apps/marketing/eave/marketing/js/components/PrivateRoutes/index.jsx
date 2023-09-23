import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';

import useUser from '../../hooks/useUser';

function PrivateRoutes() {
  const { user } = useUser();
  const { isAuthenticated } = user;

  return (
    isAuthenticated ? <Outlet /> : <Navigate to="/" />
  );
}

export default PrivateRoutes;
