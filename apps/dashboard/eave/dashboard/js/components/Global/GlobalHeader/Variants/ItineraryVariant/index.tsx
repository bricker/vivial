import { RootState } from "$eave-dashboard/js/store";
import { getTotalCost } from "$eave-dashboard/js/util/currency";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useSelector } from "react-redux";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
import CheckoutReservation from "$eave-dashboard/js/components/CheckoutReservation";
import StripeBadge from "$eave-dashboard/js/components/CheckoutReservation/StripeBadge";
import VivialLogo from "$eave-dashboard/js/components/Logo";
import Modal from "$eave-dashboard/js/components/Modal";
import Typography from "@mui/material/Typography";
import Header from "../../Shared/Header";

const BookButton = styled(PrimaryButton)(() => ({
  height: 35,
  width: 84,
}));

const Cost = styled("span")(() => ({
  fontWeight: 600,
}));

const ItineraryVariant = () => {
  const [bookingOpen, setBookingOpen] = useState(false);
  const outing = useSelector((state: RootState) => state.outing.details);
  const hasCost = !!outing?.costBreakdown?.totalCostCents;

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  return (
    <Header>
      <VivialLogo hideText={hasCost} />
      {hasCost && (
        <>
          <Typography variant="subtitle1">
            Total: <Cost>{getTotalCost(outing)}</Cost>
          </Typography>
          <BookButton onClick={toggleBookingOpen}>Book</BookButton>
          <Modal
            title="Booking Info"
            onClose={toggleBookingOpen}
            open={bookingOpen}
            badge={<StripeBadge />}
            padChildren={false}
          >
            <CheckoutReservation outingId={outing.id} />
          </Modal>
        </>
      )}
    </Header>
  );
};

export default ItineraryVariant;
