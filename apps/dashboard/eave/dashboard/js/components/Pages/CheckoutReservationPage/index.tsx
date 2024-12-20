import { AppRoute } from "$eave-dashboard/js/routes";
import React, { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import CheckoutReservation from "../../CheckoutReservation";
import { useInitiateBookingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { useDispatch } from "react-redux";
import { CircularProgress, styled, Typography } from "@mui/material";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { setBookingDetails } from "$eave-dashboard/js/store/slices/bookingSlice";
import { loadStripe, type Appearance, type CssFontSource, type CustomFontSource } from "@stripe/stripe-js";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { colors } from "$eave-dashboard/js/theme/colors";
import { Elements } from "@stripe/react-stripe-js";
import CheckoutForm from "../../CheckoutReservation";
import { myWindow } from "$eave-dashboard/js/types/window";
import CenteringContainer from "../../CenteringContainer";
import CheckoutFormStripeElementsProvider from "../../CheckoutReservation";

const CheckoutReservationPage = () => {
  const params = useParams();
  const outingId = params["outingId"]!;
  return <CheckoutFormStripeElementsProvider outingId={outingId} />;
};

export default CheckoutReservationPage;
