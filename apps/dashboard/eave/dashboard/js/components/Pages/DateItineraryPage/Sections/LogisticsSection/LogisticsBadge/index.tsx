import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getDayOfWeek } from "$eave-dashboard/js/util/date";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React from "react";

const Badge = styled("div")(() => ({
  position: "absolute",
  left: 32,
  bottom: -63,
  zIndex: 1,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
}));

const Weekday = styled(Typography)(() => ({
  fontSize: rem("10px"),
  lineHeight: rem("12px"),
  fontWeight: 500,
  textTransform: "uppercase",
  marginBottom: 3,
}));

const DateText = styled(Typography)(({ theme }) => ({
  color: theme.palette.background.paper,
  fontSize: rem("18px"),
  lineHeight: rem("22px"),
  fontWeight: 600,
}));

const Circle = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  width: 39,
  height: 39,
  borderRadius: "50%",
  filter: "drop-shadow(0px 4px 4px rgba(0, 0, 0, 0.25))",
}));

const Connector = styled("div")(() => ({
  height: 48,
  width: 3,
  background: "linear-gradient(0deg, rgba(209,89,27,1) 0%, rgba(230,240,37,1) 100%)",
}));

interface LogisticsBadgeProps {
  startTime: Date;
}

const LogisticsBadge = ({ startTime }: LogisticsBadgeProps) => {
  return (
    <Badge>
      <Weekday>{getDayOfWeek(startTime)}</Weekday>
      <Circle>
        <DateText>{startTime.getDate()}</DateText>
      </Circle>
      <Connector />
    </Badge>
  );
};

export default LogisticsBadge;
