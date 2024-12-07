import { AppRoute } from "$eave-dashboard/js/routes";
import { colors } from "$eave-dashboard/js/theme/colors";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { styled, Typography } from "@mui/material";
import React from "react";
import { useNavigate } from "react-router-dom";
import HighlightButton from "../../Buttons/HighlightButton";
import CalendarCheckIcon from "../../Icons/CalendarCheckIcon";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  width: "100%",
  display: "flex",
  flexDirection: "row",
  justifyContent: "center",
}));

const ContentContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 32,
  maxWidth: 450,
}));

const ButtonsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  gap: 8,
}));

const TitleContainer = styled("div")(({ theme }) => ({
  color: theme.palette.text.primary,
  display: "flex",
  flexDirection: "row",
  gap: 8,
  alignItems: "center",
}));

const BookedContainer = styled(Paper)(() => ({
  paddingBottom: 0,
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const Divider = styled("div")(() => ({
  borderColor: colors.midGreySecondaryField,
  borderStyle: "solid",
  width: "100%",
  borderWidth: 1,
}));

const ConfirmationsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 24,
}));

const ConfirmationOptionContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  gap: 13,
  padding: 8,
}));

const LogoContainer = styled("div")<{ padding: number; backgroundColor: string }>(({ padding, backgroundColor }) => ({
  borderRadius: 10,
  width: "40%",
  aspectRatio: 3.4,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  backgroundColor,
  padding,
}));

const LogoImage = styled("img")(() => ({
  height: "100%",
}));

interface ConfirmationOptionDetail {
  logoUri: string;
  alt: string;
  bgColor: string;
  text: string;
  padding: number;
}

const ConfirmationOption = ({ option }: { option: ConfirmationOptionDetail }) => {
  return (
    <ConfirmationOptionContainer>
      <LogoContainer backgroundColor={option.bgColor} padding={option.padding}>
        <LogoImage alt={option.alt} src={option.logoUri} />
      </LogoContainer>
      <Typography variant="body1">{option.text}</Typography>
    </ConfirmationOptionContainer>
  );
};

const confirmationOptions: ConfirmationOptionDetail[] = [
  {
    logoUri: imageUrl("vivial-word-logo.png"),
    alt: "Vivial",
    bgColor: colors.vivialYellow,
    text: "for a itinerary confirmation and receipt (if applicable).",
    padding: 10,
  },
  {
    logoUri: imageUrl("opentable-logo.png"),
    alt: "Opentable",
    bgColor: "#DA3644",
    text: "for your reservation confirmation.",
    padding: 8,
  },
  {
    logoUri: imageUrl("eventbrite-logo.png"),
    alt: "Eventbrite",
    bgColor: "#F05537",
    text: "for your tickets and event confirmation.",
    padding: 12,
  },
];

const CheckoutCompletePage = () => {
  const navigate = useNavigate();

  const handleNewDateClick = () => {
    navigate(AppRoute.root);
  };

  const handleViewPlansClick = () => {
    navigate(AppRoute.plans);
  };

  return (
    <PageContainer>
      <ContentContainer>
        <BookedContainer>
          <TitleContainer>
            <CalendarCheckIcon />
            <Typography variant="h3" sx={{ color: "white" }}>
              You're all booked!
            </Typography>
          </TitleContainer>
          <Typography variant="subtitle1">
            Check your inbox. Depending on your plans, you may see confirmations from the following:
          </Typography>
          <Divider />
          <ConfirmationsContainer>
            {confirmationOptions.map((option) => (
              <ConfirmationOption option={option} />
            ))}
          </ConfirmationsContainer>
        </BookedContainer>
        <ButtonsContainer>
          <HighlightButton highlightColor={colors.vivialYellow} highlighted onClick={handleNewDateClick}>
            🎲 New date
          </HighlightButton>
          <HighlightButton highlightColor={colors.pureWhite} highlighted onClick={handleViewPlansClick}>
            View upcoming plans
          </HighlightButton>
        </ButtonsContainer>
      </ContentContainer>
    </PageContainer>
  );
};

export default CheckoutCompletePage;
