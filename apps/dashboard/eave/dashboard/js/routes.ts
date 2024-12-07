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
  bookingConfirmation: "/booking-confirmation",
  payment: "/payment-example",
  accountPreferences: "/account/preferences",
  passwordReset: "/account/password",
  itinerary: "/itinerary",
};
