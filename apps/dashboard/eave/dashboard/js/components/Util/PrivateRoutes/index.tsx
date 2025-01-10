import { SearchParam } from "$eave-dashboard/js/routes";
import React from "react";
import { Navigate, Outlet } from "react-router-dom";

export const PrivateRoutes = ({ hasPermissions, redirectPath }: { hasPermissions: boolean; redirectPath: string }) => {
  if (hasPermissions) {
    return <Outlet />;
  }

  const returnPath = encodeURIComponent(window.location.pathname + window.location.search);

  const [pathname, searchParams] = redirectPath.split("?");
  const search = new URLSearchParams(searchParams);

  search.set(SearchParam.redirect, returnPath);

  return <Navigate replace to={{ pathname, search: `?${search.toString()}` }} />;
};
