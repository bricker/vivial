import VivialLogo from "$eave-dashboard/js/components/Logo";
import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { formatTotalCost, hasUnbookableCost } from "$eave-dashboard/js/util/currency";
import { styled } from "@mui/material";

import React, { useCallback } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

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
  const navigate = useNavigate();

  const handleBook = useCallback(() => {
    if (outing?.id) {
      const reservePath = routePath(AppRoute.checkoutReserve, { outingId: outing.id });
      navigate(reservePath);
    }
  }, [outing]);

  if (!outing) {
    return null;
  }

  const isUnbookable = hasUnbookableCost(outing);
  const costHeader = isUnbookable ? "Due Today" : "Total";
  const cost = isUnbookable ? "$0.00" : formatTotalCost(outing.costBreakdown);

  return (
    <Header>
      <VivialLogo hideText />
      <Typography variant="subtitle1">
        {costHeader}: <Cost>{cost}</Cost>
      </Typography>
      <BookButton onClick={handleBook}>Book</BookButton>
    </Header>
  );
};

export default ItineraryVariant;
