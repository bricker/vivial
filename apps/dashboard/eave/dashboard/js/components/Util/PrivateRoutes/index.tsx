import React from "react";
import { Navigate, Outlet } from "react-router-dom";

export const PrivateRoutes = ({ hasPermissions, redirectPath }: { hasPermissions: boolean; redirectPath: string }) => {
  return hasPermissions ? <Outlet /> : <Navigate to={redirectPath} />;
};
