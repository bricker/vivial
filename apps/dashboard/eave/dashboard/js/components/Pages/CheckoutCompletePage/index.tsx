import { AppRoute } from "$eave-dashboard/js/routes";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { useConfirmBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { colors } from "$eave-dashboard/js/theme/colors";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { CircularProgress, Divider, Typography, styled } from "@mui/material";
import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
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
    text: "for an itinerary confirmation and receipt (if applicable).",
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
  const params = useParams();
  const bookingId = params["bookingId"];

  if (!bookingId) {
    console.error("Invalid booking ID");
    return null;
  }

  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [confirmBooking, { isLoading: confirmBookingIsLoading, data: confirmBookingData, error: confirmBookingError }] =
    useConfirmBookingMutation();

  // const paymentIntentId = searchParams.get(SearchParam.stripePaymentIntentId);
  // const clientSecret = searchParams.get(SearchParam.stripePaymentIntentClientSecret);
  // const redirectStatus = searchParams.get(SearchParam.stripeRedirectStatus);

  useEffect(() => {
    void confirmBooking({
      input: {
        bookingId: bookingId,
      },
    });
  }, []);

  if (confirmBookingIsLoading) {
    return (
      <>
        <CircularProgress color="secondary" />
      </>
    );
  }

  if (confirmBookingError) {
    // TODO: Better error handling
    // 500 error
    console.error("Unexected Graphql result");
    return null;
  }

  if (!confirmBookingData) {
    // TODO: Better error handling
    console.error("confirmBooking data error");
    return null;
  }

  switch (confirmBookingData.viewer.__typename) {
    case "AuthenticatedViewerMutations": {
      const resp = confirmBookingData.viewer.confirmBooking;
      switch (resp?.__typename) {
        case "ConfirmBookingSuccess":
          break;
        case "ConfirmBookingFailure":
          switch (resp.failureReason) {
            default:
              console.warn("Unhandled case for CreateBookingFailure", resp.failureReason);
              break;
          }
          return;
        default:
          console.error("Unexected Graphql result");
          return;
      }
      // allow success case to continue execution
      break;
    }
    case "UnauthenticatedViewer":
      dispatch(loggedOut());
      window.location.assign(AppRoute.logout);
      return;
    default:
      console.error("Unexected Graphql result");
      return;
  }

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
              <ConfirmationOption key={option.text} option={option} />
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
