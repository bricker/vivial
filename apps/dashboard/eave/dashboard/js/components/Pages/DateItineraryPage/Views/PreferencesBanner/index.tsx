import CloseButton from "$eave-dashboard/js/components/Buttons/CloseButton";
import ArrowRightIcon from "$eave-dashboard/js/components/Icons/ArrowRightIcon";
import { AppRoute, ItineraryPageVariant, SearchParam, SignUpPageVariant, routePath } from "$eave-dashboard/js/routes";
import { RootState } from "$eave-dashboard/js/store";
import { colors } from "$eave-dashboard/js/theme/colors";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { Typography, keyframes, styled } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate, useSearchParams } from "react-router-dom";

const BannerContainer = styled("div")<{ open: boolean }>(({ theme, open }) => ({
  display: open ? "flex" : "none",
  backgroundColor: theme.palette.accent[1],
  alignItems: "center",
  justifyContent: "flex-start",
  padding: 16,
}));

const AlignedCloseButton = styled(CloseButton)(() => ({
  alignSelf: "flex-start",
}));

const TextContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
  padding: 16,
}));

const BannerText = styled(Typography)(({ theme }) => ({
  fontFamily: fontFamilies.quicksand,
  color: theme.palette.field.primary,
}));

const BannerTitle = styled(BannerText)(() => ({
  fontSize: rem(24),
}));

const pulse = keyframes`
0% {
  transform: scale(1);
}
50% {
  transform: scale(1.2);
}
100% {
  transform: scale(1);
}
`;

const AnimatedDiv = styled("div")(() => ({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  animation: `${pulse} 2s linear infinite`,
}));

const PreferencesBanner = () => {
  const navigate = useNavigate();
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);

  const [searchParams, _] = useSearchParams();
  const [prefsBannerOpen, setPrefsBannerOpen] = useState(false);

  const handleBannerClick = () => {
    navigate(
      routePath({ route: AppRoute.signup, searchParams: { [SearchParam.variant]: SignUpPageVariant.MultiReroll } }),
    );
  };

  useEffect(() => {
    if (!isLoggedIn && searchParams.get(SearchParam.variant) === ItineraryPageVariant.PreferencesBanner) {
      setPrefsBannerOpen(true);
    }
  }, [searchParams, isLoggedIn]);
  return (
    <BannerContainer open={prefsBannerOpen} onClick={handleBannerClick}>
      <AlignedCloseButton iconColor={colors.grey[800]} onClick={() => setPrefsBannerOpen(false)} />
      <TextContainer>
        <BannerTitle variant="h4">🎯 Not quite right?</BannerTitle>
        <BannerText variant="body1">Update your preferences for personalized recommendations.</BannerText>
      </TextContainer>
      <AnimatedDiv>
        <ArrowRightIcon />
      </AnimatedDiv>
    </BannerContainer>
  );
};

export default PreferencesBanner;
