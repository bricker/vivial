import { Outing } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { useListBookedOutingsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { CircularProgress, Paper as MuiPaper, Typography, styled } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PrimaryButton from "../../Buttons/PrimaryButton";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: 16,
}));

const OutingGroupContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
}));

const PlansContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 32,
}));

const CenteredArea = styled("div")(() => ({
  display: "flex",
  width: "100%",
  height: rem("128px"),
  justifyContent: "center",
  alignItems: "center",
}));

const CtaContainer = styled(Paper)(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const CenteredText = styled(Typography)(() => ({
  textAlign: "center",
}));

const ErrorMessage = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  textAlign: "center",
  fontSize: "inherit",
  lineHeight: "inherit",
}));

const Title = styled(Typography)(({ theme }) => ({
  color: theme.palette.primary.main,
}));

// couldnt use our own Paper and set the padding to 0
const DetailsPaper = styled(MuiPaper)(({ theme }) => ({
  padding: 0,
  borderRadius: "14.984px",
  background: `linear-gradient(180deg, ${theme.palette.background.paper} 75.85%, rgba(85, 88, 14, 0.10) 190.15%)`,
  boxShadow: `0px 4px 4px 0px rgba(0, 0, 0, 0.25)`,
}));

const DetailsTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  color: theme.palette.text.primary,
}));

const DetailsImage = styled("img")(() => ({
  borderRadius: 10,
  maxWidth: "50%",
}));

const OutingContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  gap: 18,
  padding: 16,
  alignItems: "center",
  justifyContent: "space-around",
}));

const OutingDetailsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const NewDateCta = () => {
  // TODO: wtf does button do
  return (
    <CtaContainer>
      <CenteredText variant="subtitle2">😢 No upcoming plans. Let's fix that</CenteredText>
      <PrimaryButton onClick={() => {}} fullWidth>
        🎲 New date
      </PrimaryButton>
    </CtaContainer>
  );
};

const OutingDetails = ({ outing }: { outing: Outing }) => {
  const imgUri = outing.activity?.photos?.coverPhotoUri || outing.restaurant?.photos?.coverPhotoUri;
  // TODO: convert outing times to local time
  const dateDayString = outing.activityStartTime || outing.restaurantArrivalTime;
  if (!dateDayString) {
    // cant show much detail if there's no activity or restaurant
    return <></>;
  }
  const dateDay = new Date(dateDayString);
  const formattedDay = new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric" }).format(
    dateDay,
  );
  return (
    <DetailsPaper>
      <OutingContainer>
        <OutingDetailsContainer>
          <DetailsTitle variant="subtitle2">{formattedDay}</DetailsTitle>
          {outing.restaurantArrivalTime && outing.restaurant && (
            <Typography variant="subtitle1">
              {new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(
                new Date(outing.restaurantArrivalTime),
              )}
              <br />
              {outing.restaurant.name}
            </Typography>
          )}
          {outing.activityStartTime && outing.activity && (
            <Typography variant="subtitle1">
              {new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(
                new Date(outing.activityStartTime),
              )}
              <br />
              {outing.activity.name}
            </Typography>
          )}
        </OutingDetailsContainer>
        {imgUri && <DetailsImage alt="" src={imgUri} />}
      </OutingContainer>
    </DetailsPaper>
  );
};

const PlansPage = () => {
  const { data, isLoading, isError } = useListBookedOutingsQuery({});
  const navigate = useNavigate();
  const [upcomingOutings, setUpcomingOutings] = useState<Outing[]>(() => []);
  const [pastOutings, setPastOutings] = useState<Outing[]>(() => []);

  useEffect(() => {
    switch (data?.viewer.__typename) {
      case "AuthenticatedViewerQueries": {
        const now = new Date();
        const outings = data.viewer.bookedOutings;
        const past = [];
        const upcoming = [];
        for (const outing of outings) {
          if (
            (outing.activityStartTime && new Date(outing.activityStartTime) > now) ||
            (outing.restaurantArrivalTime && new Date(outing.restaurantArrivalTime) > now)
          ) {
            upcoming.push(outing);
          } else {
            past.push(outing);
          }
        }
        setUpcomingOutings(upcoming);
        setPastOutings(past);
        break;
      }
      case "UnauthenticatedViewer":
        navigate(AppRoute.login);
        break;
      default:
        break;
    }
  }, [data]);

  return (
    <PageContainer>
      <PlansContainer>
        {isError ? (
          <CenteredArea>
            <ErrorMessage variant="subtitle2">
              We were unable to load your plan history.
              <br />
              Please try again later.
            </ErrorMessage>
          </CenteredArea>
        ) : (
          <>
            <OutingGroupContainer>
              <Title variant="h4">Upcoming plans</Title>
              {upcomingOutings.length > 0 ? (
                upcomingOutings.map((outing) => {
                  return <OutingDetails key={outing.id} outing={outing} />;
                })
              ) : isLoading ? (
                <CenteredArea>
                  <CircularProgress color="secondary" />
                </CenteredArea>
              ) : (
                <NewDateCta />
              )}
            </OutingGroupContainer>

            {pastOutings.length > 0 && (
              <OutingGroupContainer>
                <Title variant="h4">Past plans</Title>
                {pastOutings.map((outing) => {
                  return <OutingDetails key={outing.id} outing={outing} />;
                })}
              </OutingGroupContainer>
            )}
          </>
        )}
      </PlansContainer>
    </PageContainer>
  );
};

export default PlansPage;
