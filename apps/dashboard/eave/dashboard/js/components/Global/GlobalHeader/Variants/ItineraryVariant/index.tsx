import VivialLogo from "$eave-dashboard/js/components/Logo";
import { AppRoute } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";

import { styled } from "@mui/material";
import React, { useCallback } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { getFormattedTotalCost } from "$eave-dashboard/js/components/Pages/DateItineraryPage/helpers";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
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
  const outing = useSelector((state: RootState) => state.outing.details);
  const cost = getFormattedTotalCost(outing);
  const navigate = useNavigate();

  const handleBook = useCallback(() => {
    if (outing) {
      navigate(`${AppRoute.checkoutReserve}/${outing.id}`);
    }
  }, [outing]);

  return (
    <Header>
      <VivialLogo hideText />
      {cost && (
        <Typography variant="subtitle1">
          Total: <Cost>{cost}</Cost>
        </Typography>
      )}
      <BookButton onClick={handleBook} disabled={!outing}>
        Book
      </BookButton>
    </Header>
  );
};

export default ItineraryVariant;
