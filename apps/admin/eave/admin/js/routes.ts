export enum AppRoute {
  root = "/",
  bookingEdit = "/bookings/:bookingId/edit",
}

export function routePath(route: AppRoute, pathParams?: { [key: string]: string }): string {
  let filledRoute = route.toString();

  if (pathParams) {
    for (const [paramName, paramValue] of Object.entries(pathParams)) {
      filledRoute = filledRoute.replaceAll(new RegExp(`/:${paramName}/?$`, "g"), `/${paramValue}`);
    }
  }

  return filledRoute;
}
