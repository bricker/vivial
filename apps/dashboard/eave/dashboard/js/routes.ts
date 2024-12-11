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
  bookingConfirmation: "/booking-confirmation",
  payment: "/payment-example",
  accountPreferences: "/account/preferences",
  passwordReset: "/account/password",
  itinerary: "/itinerary",
  checkout: "/checkout/reserve",
};
