import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';

import useUser from '../../hooks/useUser';

function PrivateRoutes() {
  const { isLoggedIn } = useUser();
  return (
    isLoggedIn ? <Outlet /> : <Navigate to="/" />
  );
}

export default PrivateRoutes;
