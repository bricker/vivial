import { Outing } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute } from "$eave-dashboard/js/routes";
import { useListBookedOutingsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { CircularProgress, Typography, styled } from "@mui/material";
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

const LoadingArea = styled("div")(() => ({
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

const ErrorMessage = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginLeft: 4,
  fontSize: "inherit",
  lineHeight: "inherit",
}));

const Title = styled(Typography)(({ theme }) => ({
  color: theme.palette.primary.main,
}));

const NewDateCta = () => {
  // TODO: wtf does button do
  return (
    <CtaContainer>
      <Typography variant="subtitle2">😢 No upcoming plans. Let's fix that</Typography>
      <PrimaryButton onClick={() => {}} fullWidth>
        🎲 New date
      </PrimaryButton>
    </CtaContainer>
  );
};

const OutingDetails = () => {
  return <div>todo</div>;
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
          <div>TODO: better error ui</div>
        ) : (
          <>
            <OutingGroupContainer>
              <Title variant="button">Upcoming plans</Title>
              {upcomingOutings.length > 0 ? (
                upcomingOutings.map((outing) => {
                  return <OutingDetails key={outing.id} />;
                })
              ) : isLoading ? (
                <LoadingArea>
                  <CircularProgress color="secondary" />
                </LoadingArea>
              ) : (
                <NewDateCta />
              )}
            </OutingGroupContainer>

            {pastOutings.length > 0 && (
              <OutingGroupContainer>
                <Title variant="button">Past plans</Title>
                {pastOutings.map((outing) => {
                  return <OutingDetails key={outing.id} />;
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
