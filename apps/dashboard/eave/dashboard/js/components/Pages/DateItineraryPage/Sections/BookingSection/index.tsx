import { useGetOutingPreferencesQuery, usePlanOutingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import { formatBaseCost, formatFeesAndTaxes, formatTotalCost } from "$eave-dashboard/js/util/currency";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
import RerollButton from "$eave-dashboard/js/components/Buttons/RerollButton";
import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import Typography from "@mui/material/Typography";
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

const ActionButtons = styled("div")(() => ({
  marginTop: 24,
  display: "flex",
}));

const BookButton = styled(PrimaryButton)(() => ({
  marginLeft: 17.5,
}));

const Error = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginTop: 24,
  textAlign: "left",
}));

const BookingSection = ({ viewOnly }: { viewOnly?: boolean }) => {
  const [planOuting, { data: planOutingData, isLoading: planOutingLoading }] = usePlanOutingMutation();
  const { data: outingPreferencesData } = useGetOutingPreferencesQuery({});
  const outing = useSelector((state: RootState) => state.outing.details);
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const userPreferences = useSelector((state: RootState) => state.outing.preferenes.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferenes.partner);
  const [, setBookingOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  if (!outing) {
    console.warn("No outing available in store.");
    return null;
  }

  const activityPlan = outing.activityPlan;
  const reservation = outing.reservation;

  const handleReroll = useCallback(async () => {
    const groupPreferences = getPreferenceInputs(
      userPreferences,
      partnerPreferences,
      outingPreferencesData?.activityCategoryGroups,
      outingPreferencesData?.restaurantCategories,
    );
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
  }, [outingPreferencesData, userPreferences, partnerPreferences, outing]);

  // const toggleBookingOpen = useCallback(() => {
  //   setBookingOpen(!bookingOpen);
  // }, [bookingOpen]);

  const handleBookClick = useCallback(() => {
    navigate(routePath(AppRoute.checkoutReserve, { outingId: outing.id }));

    // if (isLoggedIn) {
    //   toggleBookingOpen();
    // } else {
    //   const returnPath = encodeURIComponent(routePath(AppRoute.checkoutReserve, { outingId: outing.id }));
    //   navigate({
    //     pathname: AppRoute.signup,
    //     search: `?${SearchParam.redirect}=${returnPath}`,
    //   });
    // }
  }, [isLoggedIn, outing]);

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
        {activityPlan && activityPlan.costBreakdown.totalCostCents > 0 && (
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
          <ActionButtons>
            <RerollButton onReroll={handleReroll} loading={planOutingLoading} />
            <BookButton onClick={handleBookClick} fullWidth>
              Book
            </BookButton>
          </ActionButtons>
        </>
      )}
      {errorMessage && <Error>ERROR: {errorMessage}</Error>}
      {/* <Modal
        title="Booking Info"
        onClose={toggleBookingOpen}
        open={bookingOpen}
        badge={<StripeBadge />}
        padChildren={false}
      >
        <CheckoutReservation outingId={outing.id} />
      </Modal> */}
    </Section>
  );
};

export default BookingSection;
