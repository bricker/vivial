export enum SearchParam {
  variant = "v",
  redirect = "r",
  outingId = "oid",

  // These come from Stripe and cannot be changed.
  stripePaymentIntentId = "payment_intent",
  stripePaymentIntentClientSecret = "payment_intent_client_secret",
  stripeRedirectStatus = "redirect_status",
}

export enum DateSurveyPageVariant {
  PreferencesOpen = "po",
}

export enum SignUpPageVariant {
  MultiReroll = "mr",
}

export enum ItineraryPageVariant {
  AutoRoll = "ar",
}

export const ITINERARY_PREFIX = "/itinerary";

export enum AppRoute {
  root = "/",
  login = "/login",
  logout = "/logout",
  forgotPassword = "/login/password",
  signup = "/signup",
  account = "/account",
  plans = "/plans",
  planDetails = "/plans/:bookingId",
  help = "/help",
  terms = "/terms",
  privacy = "/privacy",
  accountPreferences = "/account/preferences",
  passwordReset = "/account/password",
  billing = "/account/billing",
  checkoutComplete = "/checkout/complete/:bookingId",
  checkoutReserve = "/checkout/reserve/:outingId",
  itinerary = `${ITINERARY_PREFIX}/:outingId`,
}

export function routePath({
  route,
  pathParams,
  searchParams,
}: {
  route: AppRoute;
  pathParams?: { [key: string]: string };
  searchParams?: { [key: string]: string };
}): string {
  let filledRoute = route.toString();

  if (pathParams) {
    for (const [paramName, paramValue] of Object.entries(pathParams)) {
      filledRoute = filledRoute.replaceAll(new RegExp(`/:${paramName}/?$`, "g"), `/${paramValue}`);
    }
  }

  if (searchParams) {
    const urlParams = new URLSearchParams(searchParams);
    filledRoute = `${filledRoute}?${urlParams.toString()}`;
  }

  return filledRoute;
}

export interface NavigationState {
  scrollBehavior: ScrollBehavior;
}
