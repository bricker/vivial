import { SearchParam } from "$eave-dashboard/js/routes";
import React from "react";
import { Navigate, Outlet } from "react-router-dom";

export const PrivateRoutes = ({ hasPermissions, redirectPath }: { hasPermissions: boolean; redirectPath: string }) => {
  if (hasPermissions) {
    return <Outlet />;
  }

  const returnPath = encodeURIComponent(window.location.pathname + window.location.search);

  // FIXME: This assumes that `redirectPath` doesn't have any search params.
  return <Navigate to={{ pathname: redirectPath, search: `?${SearchParam.redirect}=${returnPath}` }} />;
};
