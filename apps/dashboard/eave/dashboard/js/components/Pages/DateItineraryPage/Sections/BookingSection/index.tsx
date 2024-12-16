import { useGetOutingPreferencesQuery, usePlanOutingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import { getBaseCost, getFees, getTotalCost } from "$eave-dashboard/js/util/currency";
import { getPreferenceInputs } from "$eave-dashboard/js/util/preferences";
import { getRegionIds } from "$eave-dashboard/js/util/region";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
import RerollButton from "$eave-dashboard/js/components/Buttons/RerollButton";
import CheckoutReservation from "$eave-dashboard/js/components/CheckoutReservation";
import StripeBadge from "$eave-dashboard/js/components/CheckoutReservation/StripeBadge";
import Modal from "$eave-dashboard/js/components/Modal";
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
  const userPreferences = useSelector((state: RootState) => state.outing.preferenes.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferenes.partner);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const hasCost = !!outing?.costBreakdown?.totalCostCents;
  const activity = outing?.activity;
  const restaurant = outing?.restaurant;

  const handleReroll = useCallback(async () => {
    if (outing) {
      const groupPreferences = getPreferenceInputs(
        userPreferences,
        partnerPreferences,
        outingPreferencesData?.activityCategoryGroups,
        outingPreferencesData?.restaurantCategories,
      );
      const input = {
        startTime: new Date(outing.restaurantArrivalTime || "").toISOString(),
        searchAreaIds: getRegionIds(outing),
        budget: outing.survey.budget,
        headcount: outing.survey.headcount,
        groupPreferences,
      };
      await planOuting({ input });
    }
  }, [outingPreferencesData, userPreferences, partnerPreferences, outing]);

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  useEffect(() => {
    if (planOutingData) {
      if (planOutingData.planOuting?.__typename === "PlanOutingSuccess") {
        const newOuting = planOutingData.planOuting.outing;
        setBookingOpen(false);
        dispatch(plannedOuting({ outing: newOuting }));
        navigate(`${AppRoute.itinerary}/${newOuting.id}`);
      } else {
        setErrorMessage("There was an issue planning your outing. Reach out to friends@vivialapp.com for assistance.");
      }
    }
  }, [planOutingData]);

  if (outing) {
    return (
      <Section>
        <VivialBadge />
        <Header>
          <Typography variant="inherit">Total Costs</Typography>
          <Typography variant="inherit">{getTotalCost(outing)}</Typography>
        </Header>
        <CostBreakdown>
          {restaurant && restaurant.reservable && (
            <>
              <CostItem>{restaurant.name} Reservations ...</CostItem>
              <CostItem>$0.00</CostItem>
            </>
          )}
          {activity && hasCost && (
            <>
              <CostItem>{activity.name} Tickets ...</CostItem>
              <CostItem>{getBaseCost(outing)}</CostItem>
              <CostItem>Service Fees & Taxes via Eventbrite ...</CostItem>
              <CostItem>{getFees(outing)}</CostItem>
            </>
          )}
          <CostItem>Service Fees via Vivial ...</CostItem>
          <CostItem bold>FREE</CostItem>
        </CostBreakdown>
        {!viewOnly && (
          <>
            <ActionButtons>
              <RerollButton onReroll={handleReroll} loading={planOutingLoading} />
              <BookButton onClick={toggleBookingOpen} fullWidth>
                Book
              </BookButton>
            </ActionButtons>
          </>
        )}
        {errorMessage && <Error>ERROR: {errorMessage}</Error>}
        <Modal
          title="Booking Info"
          onClose={toggleBookingOpen}
          open={bookingOpen}
          badge={<StripeBadge />}
          padChildren={false}
        >
          <CheckoutReservation outingId={outing.id} />
        </Modal>
      </Section>
    );
  }
  return null;
};

export default BookingSection;
