import { AppRoute } from "$eave-dashboard/js/routes";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled, Typography } from "@mui/material";
import React from "react";
import { useNavigate } from "react-router-dom";
import HighlightButton from "../../Buttons/HighlightButton";
import CalendarCheckIcon from "../../Icons/CalendarCheckIcon";
import Paper from "../../Paper";
import VivialLogo from "../../VivialLogo";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  display: "flex",
  flexDirection: "column",
  gap: 32,
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

const Divider = styled("div")(({ theme }) => ({
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
  gap: 13,
  padding: 8,
}));

const LogoContainer = styled("div")(() => ({
  borderRadius: 10,
  width: "30%",
  aspectRatio: 0.2941,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 8,
}));

interface ConfirmationOptionDetail {
  logo: React.ReactNode;
  bgColor: string;
  text: string;
}

const ConfirmationOption = ({ option }: { option: ConfirmationOptionDetail }) => {
  return (
    <ConfirmationOptionContainer>
      <LogoContainer
        sx={{
          backgroundColor: option.bgColor,
        }}
      >
        {option.logo}
      </LogoContainer>
      <Typography variant="body1">{option.text}</Typography>
    </ConfirmationOptionContainer>
  );
};

const confirmationOptions: ConfirmationOptionDetail[] = [
  {
    logo: <VivialLogo color="black" />,
    bgColor: colors.vivialYellow,
    text: "for a itinerary confirmation and receipt (if applicable).",
  },
  {
    logoUri: "", // TODO:
    alt: "Opentable",
    bgColor: "#DA3644",
    text: "for your reservation confirmation.",
  },
  {
    logoUri: "", // TODO:
    alt: "Eventbrite",
    bgColor: "#F05537",
    text: "for your tickets and event confirmation.",
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
      <BookedContainer>
        <TitleContainer>
          <CalendarCheckIcon />
          <Typography variant="h3">You're all booked!</Typography>
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
    </PageContainer>
  );
};

export default CheckoutCompletePage;
