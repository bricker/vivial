import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import Modal from "../../Modal";

const PageContainer = styled("div")(() => ({}));

const DateItineraryPage = () => {
  const [bookingOpen, setBookingOpen] = useState(false);
  const params = useParams();
  const _outingId = params["outingId"];

  const toggleBookingOpen = useCallback(() => {
    setBookingOpen(!useParams);
  }, [useParams]);

  return (
    <PageContainer>
      <Modal title="Booking Info" onClose={toggleBookingOpen} open={bookingOpen}>
        TODO: Booking modal content goes here (pending Liam).
      </Modal>
    </PageContainer>
  );
};

export default DateItineraryPage;
