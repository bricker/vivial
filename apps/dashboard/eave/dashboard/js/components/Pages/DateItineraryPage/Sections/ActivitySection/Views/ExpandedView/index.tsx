import { type Photos } from "$eave-dashboard/js/graphql/generated/graphql";
import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import DirectionsButton from "$eave-dashboard/js/components/Buttons/DirectionsButton";
import ImageCarousel from "$eave-dashboard/js/components/Carousels/ImageCarousel";
import LongDescription from "$eave-dashboard/js/components/LongDescription";
import Typography from "@mui/material/Typography";
import BaseActivityBadge from "../../ActivityBadge";

import { parseAddress } from "$eave-dashboard/js/util/address";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { getTimeOfDay } from "$eave-dashboard/js/util/date";
import { getImgUrls } from "../../../../helpers";

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

const ExpandedView = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const startTime = new Date(outing?.activityStartTime || "");
  const activity = outing?.activity;
  const address = parseAddress(activity?.venue.location.formattedAddress);
  const directionsUri = activity?.venue.location.directionsUri;

  if (activity) {
    return (
      <ViewContainer>
        <ActivityBadge categoryGroupId={activity.categoryGroup?.id} />
        <CarouselContainer>
          <ImageCarousel imgUrls={getImgUrls(activity.photos as Photos)} />
        </CarouselContainer>
        <InfoContainer>
          <EventInfo>
            <TimeAndTickets>
              {getTimeOfDay(startTime, false)} | {outing.survey.headcount} Tickets
            </TimeAndTickets>
            <ActivityName>{activity.name}</ActivityName>
            <VenueInfo>{activity.venue.name}</VenueInfo>
            <VenueInfo>{address.street}</VenueInfo>
            <VenueInfo>
              {address.city}, {address.state}, {address.zipCode}
            </VenueInfo>
          </EventInfo>
          <ExtraInfo>
            <PoweredBy>Events powered by</PoweredBy>
            <EventbriteLogo src={imageUrl("eventbrite-logo-orange.png")} />
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
  }
  return null;
};

export default ExpandedView;
