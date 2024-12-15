import Circle from "$eave-dashboard/js/components/Shapes/Circle";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React from "react";

import {
  ARTS_GROUP_ID,
  FITNESS_GROUP_ID,
  FOOD_GROUP_ID,
  HOBBIES_GROUP_ID,
  MEDIA_GROUP_ID,
  MUSIC_GROUP_ID,
  SEASONAL_GROUP_ID,
} from "$eave-dashboard/js/util/category/constant";

const Badge = styled("div")(() => ({
  zIndex: 1,
  position: "relative",
}));

const Emoji = styled("div")(() => ({
  fontSize: "20px", // intentionally using px instead of rem here
}));

const Connector = styled("div")(() => ({
  position: "absolute",
  height: 48,
  width: 3,
  top: -48,
  left: 19.5,
  background: "linear-gradient(0deg, rgba(255,129,181,1) 0%, rgba(175,131,253,1) 100%)",
}));

interface ActivityBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  categoryGroupId?: string;
}

const emojiMap: { [key: string]: string } = {
  [SEASONAL_GROUP_ID]: "🎉",
  [FOOD_GROUP_ID]: "🍻",
  [MEDIA_GROUP_ID]: "🎞",
  [MUSIC_GROUP_ID]: "🎶",
  [ARTS_GROUP_ID]: "🎭",
  [HOBBIES_GROUP_ID]: "📚",
  [FITNESS_GROUP_ID]: "️⛰",
};

function getEmoji(categoryGroupId?: string): string {
  if (categoryGroupId) {
    return emojiMap[categoryGroupId] || "🍦";
  }
  return "🍦";
}

const ActivityBadge = ({ categoryGroupId, ...props }: ActivityBadgeProps) => {
  return (
    <Badge {...props}>
      <Connector />
      <Circle color={colors.lightPinkAccent}>
        <Emoji>{getEmoji(categoryGroupId)}</Emoji>
      </Circle>
    </Badge>
  );
};

export default ActivityBadge;
