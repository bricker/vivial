import VivialLogo from "$eave-dashboard/js/components/Logo";
import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { styled } from "@mui/material";

import React, { useCallback } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import PrimaryButton from "$eave-dashboard/js/components/Buttons/PrimaryButton";
import Header, { HeaderVariant } from "../../Shared/Header";

const BookButton = styled(PrimaryButton)(() => ({
  height: 35,
  paddingLeft: 22.5,
  paddingRight: 22.5,
}));

const ItineraryVariant = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const navigate = useNavigate();

  if (!outing) {
    return null;
  }

  return (
    <Header variant={HeaderVariant.Sticky}>
      <VivialLogo hideText />
      <RerollButton onReroll={handleReroll} loading={planOutingLoading} />
    </Header>
  );
};

export default ItineraryVariant;