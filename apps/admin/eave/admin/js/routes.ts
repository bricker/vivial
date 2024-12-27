export enum AppRoute {
  root = "/",
  bookingEdit = "/bookings/edit/:bookingId",
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
