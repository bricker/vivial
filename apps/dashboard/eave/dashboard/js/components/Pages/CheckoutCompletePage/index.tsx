import { AppRoute } from "$eave-dashboard/js/routes";
import { colors } from "$eave-dashboard/js/theme/colors";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { Divider, styled, Typography } from "@mui/material";
import React from "react";
import { useNavigate } from "react-router-dom";
import HighlightButton from "../../Buttons/HighlightButton";
import CalendarCheckIcon from "../../Icons/CalendarCheckIcon";
import LogoPill, { LogoPillAttributes, logos } from "../../LogoPill";
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

const LightDivider = styled(Divider)(() => ({
  borderColor: colors.midGreySecondaryField,
}));

const ConfirmationsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-around",
  paddingTop: 8,
  backgroundImage: `url("${imageUrl("background-line.png")}")`,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "20% 0%",
  backgroundSize: "contain",
}));

const ConfirmationOptionContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
  gap: 13,
  padding: 8,
}));

interface ConfirmationOptionDetail {
  text: string;
  attrs: LogoPillAttributes;
}

const ConfirmationOption = ({ option }: { option: ConfirmationOptionDetail }) => {
  return (
    <ConfirmationOptionContainer>
      <LogoPill attrs={option.attrs} />
      <Typography variant="body2">{option.text}</Typography>
    </ConfirmationOptionContainer>
  );
};

const confirmationOptions: ConfirmationOptionDetail[] = [
  {
    attrs: logos["vivial"]!,
    text: "for a itinerary confirmation and receipt (if applicable).",
  },
  {
    attrs: logos["opentable"]!,
    text: "for your reservation confirmation.",
  },
  {
    attrs: logos["eventbrite"]!,
    text: "for your tickets and event confirmation.",
  },
];

const CheckoutCompletePage = () => {
  // const [searchParams] = useSearchParams();

  // const paymentIntentId = searchParams.get("payment_intent");
  // const clientSecret = searchParams.get("payment_intent_client_secret");
  // const redirectStatus = searchParams.get("redirect_status");
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
          <LightDivider />
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
