import { DateSurveyPageVariant } from "./components/Pages/DateSurveyPage/constants";
import { SignUpPageVariant } from "./components/Pages/SignUpPage/constants";

export const AppRoute = {
  root: "/",
  rootPreferencesOpen: `/?v=${DateSurveyPageVariant.PreferencesOpen}`,
  login: "/login",
  logout: "/logout",
  forgotPassword: "/login/password",
  signup: "/signup",
  signupMultiReroll: `/signup?v=${SignUpPageVariant.MultiReroll}`,
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
