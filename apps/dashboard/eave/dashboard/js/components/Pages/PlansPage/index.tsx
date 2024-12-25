import type { BookingDetailsPeekFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { AppRoute, routePath } from "$eave-dashboard/js/routes";
import { loggedOut } from "$eave-dashboard/js/store/slices/authSlice";
import { useListBookedOutingsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { CircularProgress, Paper as MuiPaper, Typography, styled } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import PrimaryButton from "../../Buttons/PrimaryButton";
import Paper from "../../Paper";

const PageContainer = styled("div")(() => ({
  padding: 16,
  maxWidth: 600,
  margin: "0 auto",
}));

const BookingGroupContainer = styled("div")(() => ({
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
  height: rem(128),
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

const BookingContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  gap: 18,
  padding: 16,
  alignItems: "center",
  justifyContent: "space-around",
}));

const BookingDetailsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const NewDateCta = () => {
  const navigate = useNavigate();
  return (
    <CtaContainer>
      <CenteredText variant="subtitle2">😢 No upcoming plans. Let's fix that</CenteredText>
      <PrimaryButton onClick={() => navigate(AppRoute.root)} fullWidth>
        🎲 New date
      </PrimaryButton>
    </CtaContainer>
  );
};

const BookingDetails = ({ booking }: { booking: BookingDetailsPeekFieldsFragment }) => {
  const navigate = useNavigate();
  const imgUri = booking.photoUri;
  const dateDayString = booking.activityStartTime || booking.restaurantArrivalTime;
  if (!dateDayString) {
    // cant show much detail if there's no activity or restaurant
    return <></>;
  }
  const dateDay = new Date(dateDayString);
  const formattedDay = new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric" }).format(
    dateDay,
  );
  return (
    <DetailsPaper onClick={() => navigate(routePath(AppRoute.planDetails, { bookingId: booking.id }))}>
      <BookingContainer>
        <BookingDetailsContainer>
          <DetailsTitle variant="subtitle2">{formattedDay}</DetailsTitle>
          {booking.restaurantArrivalTime && booking.restaurantName && (
            <Typography variant="subtitle1">
              {new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(
                new Date(booking.restaurantArrivalTime),
              )}
              <br />
              {booking.restaurantName}
            </Typography>
          )}
          {booking.activityStartTime && booking.activityName && (
            <Typography variant="subtitle1">
              {new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(
                new Date(booking.activityStartTime),
              )}
              <br />
              {booking.activityName}
            </Typography>
          )}
        </BookingDetailsContainer>
        {imgUri && <DetailsImage alt="" src={imgUri} />}
      </BookingContainer>
    </DetailsPaper>
  );
};

const PlansPage = () => {
  const { data, isLoading, isError } = useListBookedOutingsQuery({});
  const dispatch = useDispatch();
  const [upcomingBookings, setUpcomingBookings] = useState<BookingDetailsPeekFieldsFragment[]>(() => []);
  const [pastBookings, setPastBookings] = useState<BookingDetailsPeekFieldsFragment[]>(() => []);

  useEffect(() => {
    switch (data?.viewer.__typename) {
      case "AuthenticatedViewerQueries": {
        const now = new Date();
        const bookings = data.viewer.bookedOutings;
        const past = [];
        const upcoming = [];
        for (const booking of bookings) {
          if (
            (booking.activityStartTime && new Date(booking.activityStartTime) > now) ||
            (booking.restaurantArrivalTime && new Date(booking.restaurantArrivalTime) > now)
          ) {
            upcoming.push(booking);
          } else {
            past.push(booking);
          }
        }
        setUpcomingBookings(upcoming);
        setPastBookings(past);
        break;
      }
      case "UnauthenticatedViewer":
        dispatch(loggedOut());
        window.location.assign(AppRoute.logout);
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
            <BookingGroupContainer>
              <Title variant="h4">Upcoming plans</Title>
              {upcomingBookings.length > 0 ? (
                upcomingBookings.map((booking) => {
                  return <BookingDetails key={booking.id} booking={booking} />;
                })
              ) : isLoading ? (
                <CenteredArea>
                  <CircularProgress color="secondary" />
                </CenteredArea>
              ) : (
                <NewDateCta />
              )}
            </BookingGroupContainer>

            {pastBookings.length > 0 && (
              <BookingGroupContainer>
                <Title variant="h4">Past plans</Title>
                {pastBookings.map((booking) => {
                  return <BookingDetails key={booking.id} booking={booking} />;
                })}
              </BookingGroupContainer>
            )}
          </>
        )}
      </PlansContainer>
    </PageContainer>
  );
};

export default PlansPage;
