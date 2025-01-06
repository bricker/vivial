export enum SearchParam {
  variant = "v",
  redirect = "r",

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

export const ITINERARY_PREFIX = "/itinerary";

export enum AppRoute {
  root = "/",
  rootPreferencesOpen = `/?${SearchParam.variant}=${DateSurveyPageVariant.PreferencesOpen}`,
  login = "/login",
  logout = "/logout",
  forgotPassword = "/login/password",
  signup = "/signup",
  signupMultiReroll = `/signup?${SearchParam.variant}=${SignUpPageVariant.MultiReroll}`,
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

export function routePath(route: AppRoute, pathParams?: { [key: string]: string }): string {
  let filledRoute = route.toString();

  if (pathParams) {
    for (const [paramName, paramValue] of Object.entries(pathParams)) {
      filledRoute = filledRoute.replaceAll(new RegExp(`/:${paramName}/?$`, "g"), `/${paramValue}`);
    }
  }

  return filledRoute;
}

export interface NavigationState {
  scrollBehavior: ScrollBehavior;
}
