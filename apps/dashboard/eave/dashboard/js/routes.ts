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
  help = "/help",
  terms = "/terms",
  privacy = "/privacy",
  accountPreferences = "/account/preferences",
  passwordReset = "/account/password",
  checkoutComplete = "/checkout/complete/:bookingId",
  checkoutReserve = "/checkout/reserve/:outingId",
  itinerary = "/itinerary",
};

export function routePath(route: AppRoute, pathParams: {[key:string]: string}): string {
  let filledRoute = route.toString();

  for (const [paramName, paramValue] of Object.entries(pathParams)) {
    filledRoute = filledRoute.replaceAll(new RegExp(`/:${paramName}/?$`, "g"), paramValue);
  }

  return filledRoute;
}
