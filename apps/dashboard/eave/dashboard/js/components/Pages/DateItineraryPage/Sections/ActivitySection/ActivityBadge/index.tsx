import Circle from "$eave-dashboard/js/components/Shapes/Circle";
import { type ActivityFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
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
  left: 18,
  background: "linear-gradient(0deg, rgba(255,129,181,1) 0%, rgba(175,131,253,1) 100%)",
}));

interface ActivityBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  activity: ActivityFieldsFragment;
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

function getEmoji(activity: ActivityFieldsFragment): string {
  const primaryTypeName = activity.primaryTypeName?.toLocaleLowerCase();
  if (primaryTypeName) {
    if (primaryTypeName.includes("bar")) {
      return "🍸";
    }
    if (primaryTypeName.includes("ice cream")) {
      return "🍦";
    }
  }
  const categoryGroupId = activity.categoryGroup?.id;
  if (categoryGroupId) {
    return emojiMap[categoryGroupId] || "🎟️";
  }
  return "🎟️";
}

const ActivityBadge = ({ activity, ...props }: ActivityBadgeProps) => {
  return (
    <Badge {...props}>
      <Connector />
      <Circle color={colors.lightPinkAccent}>
        <Emoji>{getEmoji(activity)}</Emoji>
      </Circle>
    </Badge>
  );
};

export default ActivityBadge;
