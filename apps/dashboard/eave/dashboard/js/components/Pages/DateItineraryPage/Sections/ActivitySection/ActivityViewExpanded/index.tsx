import { ActivitySource } from "$eave-dashboard/js/graphql/generated/graphql";
import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import DirectionsButton from "$eave-dashboard/js/components/Buttons/DirectionsButton";
import ImageCarousel from "$eave-dashboard/js/components/Carousels/ImageCarousel";
import LongDescription from "$eave-dashboard/js/components/LongDescription";
import Typography from "@mui/material/Typography";
import BaseActivityBadge from "../ActivityBadge";

import { imageUrl } from "$eave-dashboard/js/util/asset";
import { getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getActivityVenueName, getImgUrls, getTicketInfo } from "../../../helpers";

const ViewContainer = styled("div")(() => ({
  position: "relative",
}));

const CarouselContainer = styled("div")(() => ({
  marginBottom: 16,
}));

const ActivityBadge = styled(BaseActivityBadge)(() => ({
  position: "absolute",
  top: 0,
  left: 0,
}));

const InfoContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
  marginBottom: 16,
}));

const EventInfo = styled("div")(() => ({
  paddingRight: 16,
}));

const TimeAndTickets = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(16),
  lineHeight: rem(18),
  fontWeight: 600,
  marginBottom: 8,
}));

const ActivityName = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(16),
  lineHeight: rem(19),
  marginBottom: 8,
}));

const VenueInfo = styled(Typography)(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem(10),
  lineHeight: rem(12),
}));

const ExtraInfo = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
}));

const PoweredBy = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(10),
  lineHeight: rem(12),
  marginBottom: 2,
}));

const Notes = styled(Typography)(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem(14),
  lineHeight: rem(17),
  marginBottom: 8,
}));

const EventbriteLogo = styled("img")(() => ({
  width: 88,
  marginBottom: 8,
}));

const ActivityViewExpanded = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const startTime = outing?.activityPlan ? new Date(outing.activityPlan?.startTime) : new Date();
  const activity = outing?.activityPlan?.activity;
  const address = activity?.venue.location.address;
  const directionsUri = activity?.venue.location.directionsUri;

  if (!outing || !activity) {
    return null;
  }

  return (
    <ViewContainer>
      <ActivityBadge activity={activity} />
      <CarouselContainer>
        <ImageCarousel imgUrls={getImgUrls(activity.photos)} />
      </CarouselContainer>
      <InfoContainer>
        <EventInfo>
          <TimeAndTickets>
            {getTimeOfDay(startTime, false)} | {getTicketInfo(outing)}
          </TimeAndTickets>
          <ActivityName>{activity.name}</ActivityName>
          <VenueInfo>{getActivityVenueName(activity)}</VenueInfo>
          {address && (
            <>
              <VenueInfo>
                {address.address1} {address.address2}
              </VenueInfo>
              <VenueInfo>{[address.city, address.state, address.zipCode].filter((k) => k).join(", ")}</VenueInfo>
            </>
          )}
        </EventInfo>
        <ExtraInfo>
          {activity.source === ActivitySource.Eventbrite && (
            <>
              <PoweredBy>Events powered by</PoweredBy>
              <EventbriteLogo src={imageUrl("eventbrite-logo-orange.png")} />
            </>
          )}
          {directionsUri && <DirectionsButton uri={directionsUri} />}
        </ExtraInfo>
      </InfoContainer>
      <LongDescription>{activity.description}</LongDescription>
      {activity.doorTips && <Notes>⏰ {activity.doorTips}</Notes>}
      {activity.ticketInfo?.notes && <Notes>🎫 {activity.ticketInfo.notes}</Notes>}
      {activity.parkingTips && <Notes>🚘 Parking Tips: {activity.parkingTips}</Notes>}
      {activity.insiderTips && <Notes>🍨 Insider scoop: {activity.insiderTips}</Notes>}
    </ViewContainer>
  );
};

export default ActivityViewExpanded;
