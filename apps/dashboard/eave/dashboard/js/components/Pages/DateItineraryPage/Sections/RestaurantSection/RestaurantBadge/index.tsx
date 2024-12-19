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

const RestaurantBadge = (props: React.HTMLAttributes<HTMLDivElement>) => {
  return (
    <Badge {...props}>
      <Circle color={colors.brightOrangeAccent}>
        <Emoji>🍔</Emoji>
      </Circle>
    </Badge>
  );
};

export default RestaurantBadge;
