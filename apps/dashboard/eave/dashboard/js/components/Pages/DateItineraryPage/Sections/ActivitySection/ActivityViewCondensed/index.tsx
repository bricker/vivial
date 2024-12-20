import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getTimeOfDay } from "$eave-dashboard/js/util/date";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import { getActivityCategoryInfo, getActivityVenueName, getTicketInfo } from "../../../helpers";

import Typography from "@mui/material/Typography";
import ActivityBadge from "../ActivityBadge";

const ViewContainer = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
}));

const ImgContainer = styled("div")(() => ({
  height: 102,
  width: 184,
  minWidth: 184,
  overflow: "hidden",
  borderRadius: 10,
  marginLeft: 16,
}));

const Img = styled("img")(() => ({
  objectFit: "cover",
  minHeight: "100%",
  width: "100%",
}));

const CopyContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  marginBottom: 12,
}));

const TimeAndTicketInfo = styled("div")(() => ({
  marginLeft: 9,
}));

const Time = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  marginRight: 4,
  fontSize: rem(16),
  lineHeight: rem(19),
  fontWeight: 600,
}));

const Tickets = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontsize: rem(14),
  lineHeight: rem(17),
}));

const ActivityName = styled(Typography)(({ theme }) => ({
  color: theme.palette.common.white,
  fontSize: rem(14),
  lineHeight: rem(17),
  marginBottom: 4,
}));

const ActivityDesc = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(15),
  marginBottom: 4,
  textTransform: "capitalize",
  "&:last-of-type": {
    marginBottom: 0,
  },
}));

const ActivityViewCondensed = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const activityPlan = outing?.activityPlan;
  const startTime = activityPlan ? new Date(activityPlan.startTime) : new Date();
  const activity = activityPlan?.activity;

  if (!outing || !activity) {
    return null;
  }

  return (
    <ViewContainer>
      <div>
        <CopyContainer>
          <ActivityBadge activity={activity} />
          <TimeAndTicketInfo>
            <Time>{getTimeOfDay(startTime, false)}</Time>
            <Tickets>{getTicketInfo(outing)}</Tickets>
          </TimeAndTicketInfo>
        </CopyContainer>
        <ActivityName>{activity.name}</ActivityName>
        <ActivityDesc>{getActivityVenueName(activity)}</ActivityDesc>
        <ActivityDesc>{getActivityCategoryInfo(activity)}</ActivityDesc>
      </div>
      {activity.photos.coverPhoto && (
        <ImgContainer>
          <Img src={activity.photos.coverPhoto.src} />
        </ImgContainer>
      )}
    </ViewContainer>
  );
};

export default ActivityViewCondensed;
