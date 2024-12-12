import Modal from "$eave-dashboard/js/components/Modal";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";

const Section = styled("section")(() => ({}));

const BookingSection = () => {
  const [bookingOpen, setBookingOpen] = useState(false);

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!bookingOpen);
  }, [bookingOpen]);

  return (
    <Section>
      <Modal title="Booking Info" onClose={toggleBookingOpen} open={bookingOpen}>
        TODO: Booking modal content goes here (pending Liam).
      </Modal>
      {/* <button onClick={toggleBookingOpen}>Open Booking Modal</button> */}
    </Section>
  );
};

export default BookingSection;
