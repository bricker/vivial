import Circle from "$eave-dashboard/js/components/Shapes/Circle";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { getDate, getDayOfWeek } from "$eave-dashboard/js/util/date";
import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React from "react";

const Badge = styled("div")(() => ({
  position: "absolute",
  left: 32,
  top: 142,
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

const Date = styled(Typography)(({ theme }) => ({
  color: theme.palette.background.paper,
  fontSize: rem("18px"),
  lineHeight: rem("22px"),
  fontWeight: 600,
}));

const Connector = styled("div")(() => ({
  height: 48,
  width: 3,
  background: "linear-gradient(0deg, rgba(209,89,27,1) 0%, rgba(230,240,37,1) 100%)",
}));

interface LogisticsBadgeProps {
  startTime: Date;
  connect: boolean;
}

const LogisticsBadge = ({ startTime, connect }: LogisticsBadgeProps) => {
  return (
    <Badge>
      <Weekday>{getDayOfWeek(startTime)}</Weekday>
      <Circle color={colors.vivialYellow}>
        <Date>{getDate(startTime)}</Date>
      </Circle>
      {connect && <Connector />}
    </Badge>
  );
};

export default LogisticsBadge;
