import {
  useGetOneClickBookingCriteriaQuery,
  useInitiateAndConfirmBookingMutation,
  usePlanOutingMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import {
  OutingBudget,
  type Itinerary,
  type PaymentMethodFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import { formatBaseCost, formatFeesAndTaxes, formatTotalCost } from "$eave-dashboard/js/util/currency";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";

import EditButton from "$eave-dashboard/js/components/Buttons/EditButton";
import LoadingButton from "$eave-dashboard/js/components/Buttons/LoadingButton";
import RerollButton from "$eave-dashboard/js/components/Buttons/RerollButton";
import CheckoutFormStripeElementsProvider from "$eave-dashboard/js/components/CheckoutReservation";
import Modal from "$eave-dashboard/js/components/Modal";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { setBookingDetails } from "$eave-dashboard/js/store/slices/bookingSlice";
import { storePaymentMethods } from "$eave-dashboard/js/store/slices/paymentMethodsSlice";
import { storeReserverDetails } from "$eave-dashboard/js/store/slices/reserverDetailsSlice";
import { capitalize } from "$eave-dashboard/js/util/string";
import Typography from "@mui/material/Typography";
import OneClickBadge from "./OneClickBadge";
import VivialBadge from "./VivialBadge";

const Section = styled("section")(({ theme }) => ({
  position: "relative",
  borderTop: `1.5px solid ${theme.palette.primary.main}`,
  backgroundColor: theme.palette.background.paper,
  padding: "32px 32px 56px",
}));

const Header = styled("div")(({ theme }) => ({
  color: theme.palette.common.white,
  borderBottom: `1px solid ${colors.secondaryButtonCTA}`,
  display: "flex",
  justifyContent: "space-between",
  paddingBottom: 16,
  marginBottom: 16,
  fontSize: rem(16),
  lineHeight: rem(19),
  fontWeight: 600,
}));

const CostBreakdown = styled("div")(() => ({
  borderBottom: `1px solid ${colors.secondaryButtonCTA}`,
  paddingBottom: 16,
  display: "grid",
  gridTemplateColumns: "1fr auto",
  gridColumnGap: "8px",
}));

const CostItem = styled(Typography, {
  shouldForwardProp: (prop) => prop !== "bold",
})<{ bold?: boolean }>(({ bold }) => ({
  textAlign: "right",
  fontWeight: bold ? 700 : 400,
}));

const OneClickBooking = styled("div")(() => ({
  display: "flex",
}));

const OneClickDetails = styled("div")(() => ({
  flex: 1,
}));

const OneClickInputsContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
}));

const OneClickInputs = styled("div")(() => ({
  display: "grid",
  gridTemplateAreas: `
    'name nameVal'
    'phone phoneVal'
    'email emailVal'
    'pay payVal'
  `,
  gridColumnGap: "40px",
}));

const OneClickHeader = styled(Typography)(({ theme }) => ({
  color: theme.palette.primary.main,
  paddingTop: 18,
  marginBottom: 14,
  fontSize: rem(16),
  lineHeight: rem(19),
  fontWeight: 600,
}));

const OneClickInputName = styled(Typography, {
  shouldForwardProp: (prop) => prop !== "gridArea",
})<{ gridArea: string }>(({ gridArea }) => ({
  gridArea,
}));

const OneClickInputValue = styled(Typography, {
  shouldForwardProp: (prop) => prop !== "gridArea",
})<{ gridArea: string }>(({ gridArea }) => ({
  gridArea,
}));

const OneClickEditBtn = styled(EditButton)(() => ({
  padding: "3px 0px 16px 16px",
}));

const ActionButtons = styled("div")(() => ({
  marginTop: 24,
  display: "flex",
}));

const BookButton = styled(LoadingButton)(() => ({
  marginLeft: 17.5,
}));

const Error = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginTop: 24,
  textAlign: "left",
}));

const isPaidOuting = (itinerary: Itinerary): boolean => {
  return itinerary.costBreakdown.totalCostCents > 0;
};

const BookingSection = ({ viewOnly }: { viewOnly?: boolean }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [planOuting, { data: planOutingData, isLoading: planOutingLoading }] = usePlanOutingMutation();

  const { isLoggedIn, account } = useSelector((state: RootState) => state.auth);
  const outing = useSelector((state: RootState) => state.outing.details);
  const userPreferences = useSelector((state: RootState) => state.outing.preferenes.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferenes.partner);
  const { reserverDetails } = useSelector((state: RootState) => state.reserverDetails);
  const { paymentMethods } = useSelector((state: RootState) => state.paymentMethods);

  const [bookingOpen, setBookingOpen] = useState(false);
  const [bookButtonLoading, setBookButtonLoading] = useState(false);

  const [oneClickEligible, setOneClickEligible] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [defaultPaymentMethod, setDefaultPaymentMethod] = useState<PaymentMethodFieldsFragment | null>(null);
  useEffect(() => {
    if (paymentMethods && paymentMethods.length > 0 && paymentMethods[0]) {
      setDefaultPaymentMethod(paymentMethods[0]);
    }
  }, [paymentMethods]);

  // We only want to run this if the user is logged in.
  const { data: oneClickBookingCriteriaData } = useGetOneClickBookingCriteriaQuery({}, { skip: !isLoggedIn });
  const [initiateAndConfirmBooking] = useInitiateAndConfirmBookingMutation();

  useEffect(() => {
    if (!oneClickBookingCriteriaData) {
      return;
    }
    switch (oneClickBookingCriteriaData.viewer.__typename) {
      case "AuthenticatedViewerQueries": {
        let eligible = false;
        const defaultReserverDetails = oneClickBookingCriteriaData.viewer.reserverDetails[0];

        if (defaultReserverDetails) {
          eligible = true;
          dispatch(storeReserverDetails({ details: defaultReserverDetails }));
        }

        if (eligible && outing && isPaidOuting(outing)) {
          eligible = eligible && oneClickBookingCriteriaData.viewer.paymentMethods.length > 0;
          dispatch(storePaymentMethods({ paymentMethods: oneClickBookingCriteriaData.viewer.paymentMethods }));
        }

        setOneClickEligible(eligible);
        return;
      }
      case "UnauthenticatedViewer": {
        // Do nothing in this case - this page is allowed unauthenticated.
        return;
      }
      default: {
        console.error("Unexpected GraphQL response");
        return;
      }
    }
  }, [oneClickBookingCriteriaData]);

  const handleReroll = useCallback(async () => {
    if (outing) {
      const groupPreferences = getPreferenceInputs(userPreferences, partnerPreferences);
      await planOuting({
        input: {
          startTime: new Date(outing.survey?.startTime || outing.startTime).toISOString(),
          searchAreaIds: (outing.survey?.searchRegions || outing.searchRegions).map((r) => r.id),
          budget: outing.survey?.budget || OutingBudget.Expensive,
          headcount: outing.survey?.headcount || outing.headcount,
          groupPreferences,
          isReroll: true,
        },
      });
    }
  }, [userPreferences, partnerPreferences, outing]);

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  const handleBookClick = useCallback(async () => {
    if (!outing) {
      console.warn("No outing.");
      return;
    }

    if (!oneClickEligible || !isLoggedIn) {
      // This handles the auth redirect and return path
      navigate(routePath(AppRoute.checkoutReserve, { outingId: outing.id }));
      return;
    }

    setBookButtonLoading(true);

    const { data: initiateAndConfirmBookingData, error: initiateAndConfirmBookingError } =
      await initiateAndConfirmBooking({
        input: {
          outingId: outing.id,
          autoConfirm: true,
          paymentMethodId: paymentMethods?.[0]?.id,
        },
      });

    if (initiateAndConfirmBookingError || !initiateAndConfirmBookingData) {
      setBookButtonLoading(false);
      setErrorMessage("There was an error during booking. Please try again later.");
      return;
    }

    const viewer = initiateAndConfirmBookingData.viewer;
    switch (viewer.__typename) {
      case "AuthenticatedViewerMutations": {
        const initiateBookingResult = viewer.initiateBooking;
        switch (initiateBookingResult.__typename) {
          case "InitiateBookingSuccess": {
            const booking = initiateBookingResult.booking;
            dispatch(setBookingDetails({ bookingDetails: booking }));
            navigate(routePath(AppRoute.checkoutComplete, { bookingId: booking.id }));
            return;
          }
          case "InitiateBookingFailure": {
            console.error(`failure: ${initiateBookingResult.failureReason}`);
            setBookButtonLoading(false);
            setErrorMessage("There was an error during booking. Please try again later.");
            return;
          }
          default: {
            console.error("Unexpected graphql response type");
            setBookButtonLoading(false);
            setErrorMessage("There was an error during booking. Please try again later.");
          }
        }
        return;
      }
      case "UnauthenticatedViewer": {
        dispatch(loggedOut());
        window.location.assign(AppRoute.logout);
        return;
      }
      default: {
        console.error("Unexpected graphql response type");
        setBookButtonLoading(false);
        setErrorMessage("There was an error during booking. Please try again later.");
      }
    }
  }, [isLoggedIn, outing, oneClickEligible]);

  useEffect(() => {
    if (planOutingData) {
      switch (planOutingData.planOuting?.__typename) {
        case "PlanOutingSuccess": {
          const newOuting = planOutingData.planOuting.outing;
          setBookingOpen(false);
          dispatch(plannedOuting({ outing: newOuting }));
          navigate(routePath(AppRoute.itinerary, { outingId: newOuting.id }));
          break;
        }
        default: {
          setErrorMessage(
            "There was an issue planning your outing. Reach out to friends@vivialapp.com for assistance.",
          );
        }
      }
    }
  }, [planOutingData]);

  if (!outing) {
    return null;
  }

  const activityPlan = outing.activityPlan;
  const reservation = outing.reservation;

  let oneClickUI: React.JSX.Element | undefined;

  if (oneClickEligible && reserverDetails && account) {
    oneClickUI = (
      <OneClickBooking>
        <OneClickBadge />
        <OneClickDetails>
          <OneClickHeader>One click booking</OneClickHeader>
          <OneClickInputsContainer>
            <OneClickInputs>
              <OneClickInputName gridArea="name">Name</OneClickInputName>
              <OneClickInputValue gridArea="nameVal">
                {reserverDetails.firstName} {reserverDetails.lastName}
              </OneClickInputValue>
              <OneClickInputName gridArea="phone">Phone #</OneClickInputName>
              <OneClickInputValue gridArea="phoneVal">{reserverDetails.phoneNumber}</OneClickInputValue>
              <OneClickInputName gridArea="email">Email</OneClickInputName>
              <OneClickInputValue gridArea="emailVal">{account.email}</OneClickInputValue>

              {isPaidOuting(outing) && defaultPaymentMethod?.card && (
                <>
                  <OneClickInputName gridArea="pay">Pay with</OneClickInputName>
                  <OneClickInputValue gridArea="payVal">
                    {capitalize(defaultPaymentMethod.card.brand)} *{defaultPaymentMethod.card.last4}
                  </OneClickInputValue>
                </>
              )}
            </OneClickInputs>
            <OneClickEditBtn onClick={toggleBookingOpen} />
          </OneClickInputsContainer>
        </OneClickDetails>
      </OneClickBooking>
    );
  }

  return (
    <Section>
      <VivialBadge />
      <Header>
        <Typography variant="inherit">Total Costs</Typography>
        <Typography variant="inherit">{formatTotalCost(outing.costBreakdown)}</Typography>
      </Header>
      <CostBreakdown>
        {reservation && reservation.restaurant.reservable && (
          <>
            <CostItem>{reservation.restaurant.name} Reservations ...</CostItem>
            <CostItem>{formatTotalCost(reservation.costBreakdown)}</CostItem>
          </>
        )}
        {activityPlan && isPaidOuting(outing) && (
          <>
            <CostItem>{activityPlan.activity.name} Tickets ...</CostItem>
            <CostItem>{formatBaseCost(activityPlan.costBreakdown)}</CostItem>
            <CostItem>Service Fees & Taxes via Eventbrite ...</CostItem>
            <CostItem>{formatFeesAndTaxes(activityPlan.costBreakdown)}</CostItem>
          </>
        )}
        <CostItem>Service Fees via Vivial ...</CostItem>
        <CostItem bold>FREE</CostItem>
      </CostBreakdown>

      {!viewOnly && (
        <>
          {oneClickUI}

          <ActionButtons>
            <RerollButton onReroll={handleReroll} loading={planOutingLoading} />
            <BookButton onClick={handleBookClick} fullWidth loading={bookButtonLoading}>
              Book
            </BookButton>
          </ActionButtons>
        </>
      )}
      {errorMessage && <Error>{errorMessage}</Error>}
      {bookingOpen && (
        <Modal
          title="Booking Info"
          onClose={toggleBookingOpen}
          open={bookingOpen}
          // badge={<StripeBadge />} // Avoid a double stripe badge
          padChildren={false}
        >
          <CheckoutFormStripeElementsProvider outingId={outing.id} />;
        </Modal>
      )}
    </Section>
  );
};

export default BookingSection;
