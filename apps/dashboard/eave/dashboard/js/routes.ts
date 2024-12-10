import { SignUpPageVariant } from "./components/Pages/SignUpPage/constants";

export const AppRoute = {
  root: "/",
  login: "/login",
  logout: "/logout",
  forgotPassword: "/login/password",
  signup: "/signup",
  signupMultiReroll: `/signup?variant=${SignUpPageVariant.MultiReroll}`,
  account: "/account",
  plans: "/plans",
  help: "/help",
  terms: "/terms",
  privacy: "/privacy",
  accountPreferences: "/account/preferences",
  passwordReset: "/account/password",
  checkoutComplete: "/checkout/complete",
  checkoutReserve: "/checkout/reserve",
  itinerary: "/itinerary",
};
