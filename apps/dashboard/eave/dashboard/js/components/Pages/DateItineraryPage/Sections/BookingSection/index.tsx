import React, { useCallback, useState } from "react";
import { useSelector } from "react-redux";

import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { styled } from "@mui/material";

import CheckoutReservation from "$eave-dashboard/js/components/CheckoutReservation";
import Modal from "$eave-dashboard/js/components/Modal";

const Section = styled("section")(() => ({}));

const BadgeImg = styled("img")(() => ({
  height: rem(24),
  maxHeight: 32,
}));

const BookingSection = () => {
  const [bookingOpen, setBookingOpen] = useState(false);
  const outing = useSelector((state: RootState) => state.outing.details);
  const stripeBadge = <BadgeImg src={imageUrl("powered-by-stripe.png")} alt="powered by Stripe" />;

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  if (outing) {
    return (
      <Section>
        <Modal
          title="Booking Info"
          onClose={toggleBookingOpen}
          open={bookingOpen}
          badge={stripeBadge}
          padChildren={false}
        >
          <CheckoutReservation outingId={outing.id} />
        </Modal>
        {/* <button onClick={toggleBookingOpen}>TEMP: Open Booking Modal</button> */}
      </Section>
    );
  }
  return null;
};

export default BookingSection;
