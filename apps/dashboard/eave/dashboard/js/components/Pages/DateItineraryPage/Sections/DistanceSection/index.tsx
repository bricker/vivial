import React from "react";
import { useSelector } from "react-redux";

import { RootState } from "$eave-dashboard/js/store";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";

import Typography from "@mui/material/Typography";
import DistanceBadge from "./DistanceBadge";

const Section = styled("section")(() => ({
  display: "flex",
  alignItems: "center",
  position: "relative",
  padding: "0px 32px",
  marginBottom: 32,
}));

const DrivingTime = styled(Typography)(() => ({
  marginLeft: 12,
  fontSize: rem(14),
  lineHeight: rem(17),
  fontWeight: 500,
}));

const DistanceSection = () => {
  const outing = useSelector((state: RootState) => state.outing.details);
  const drivingDurationMinutes = outing?.travel?.durationMinutes;

  if (!outing || !drivingDurationMinutes) {
    return null;
  }

  return (
    <Section>
      <DistanceBadge />
      <DrivingTime>{drivingDurationMinutes} min drive</DrivingTime>
    </Section>
  );
};

export default DistanceSection;
