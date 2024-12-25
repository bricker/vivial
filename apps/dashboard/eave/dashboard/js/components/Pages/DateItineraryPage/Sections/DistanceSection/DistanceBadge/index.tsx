import Circle from "$eave-dashboard/js/components/Shapes/Circle";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React from "react";

const Badge = styled("div")(() => ({
  zIndex: 1,
}));

const Emoji = styled("div")(() => ({
  fontSize: "20px", // intentionally using px instead of rem here
}));

const Connector = styled("div")(() => ({
  position: "absolute",
  height: 32,
  width: 3,
  top: -32,
  left: 50,
  background: "linear-gradient(0deg, rgba(175,131,253,1) 0%, rgba(243,197,168,1) 100%)",
}));

const DistanceBadge = (props: React.HTMLAttributes<HTMLDivElement>) => {
  return (
    <Badge {...props}>
      <Connector />
      <Circle color={colors.mediumPurpleAccent}>
        <Emoji>🚗</Emoji>
      </Circle>
    </Badge>
  );
};

export default DistanceBadge;
