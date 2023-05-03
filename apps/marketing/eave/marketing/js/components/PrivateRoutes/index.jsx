import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';

import useUser from '../../hooks/useUser';

function PrivateRoutes() {
  const { isUserAuth } = useUser();
  return (
    isUserAuth ? <Outlet /> : <Navigate to="/" />
  );
}

export default PrivateRoutes;
