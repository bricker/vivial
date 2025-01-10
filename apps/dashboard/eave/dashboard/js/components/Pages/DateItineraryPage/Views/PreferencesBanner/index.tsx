import CloseButton from "$eave-dashboard/js/components/Buttons/CloseButton";
import { ItineraryPageVariant, SearchParam } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { Typography, styled } from "@mui/material";
import { ArrowRightIcon } from "@mui/x-date-pickers";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useSearchParams } from "react-router-dom";

const BannerContainer = styled("div")<{ open: boolean }>(({ theme, open }) => ({
  display: open ? "flex" : "none",
  backgroundColor: theme.palette.accent[1],
  alignItems: "center",
  justifyContent: "flex-start",
}));

const TextContainer = styled("div")(() => ({
  padding: 16,
}));

const PreferencesBanner = () => {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);

  const [searchParams, _] = useSearchParams();
  const [prefsBannerOpen, setPrefsBannerOpen] = useState(false);

  useEffect(() => {
    if (!isLoggedIn && searchParams.get(SearchParam.variant) === ItineraryPageVariant.PreferencesBanner) {
      setPrefsBannerOpen(true);
    }
  }, [searchParams, isLoggedIn]);
  return (
    <BannerContainer open={prefsBannerOpen}>
      <CloseButton onClick={() => setPrefsBannerOpen(false)} />
      <TextContainer>
        <Typography variant="h2">🎯 Not quite right?</Typography>
        <Typography variant="body1">Update your preferences for personalized recommendations.</Typography>
      </TextContainer>
      <ArrowRightIcon />
    </BannerContainer>
  );
};

export default PreferencesBanner;
