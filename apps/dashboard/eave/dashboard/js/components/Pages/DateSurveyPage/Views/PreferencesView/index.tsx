import React, { useState, useCallback } from "react";
import {
  useGetActivityCategoriesQuery,
  useGetRestaurantCategoriesQuery,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { colors } from "$eave-dashboard/js/theme/colors";
import {
  type ActivityCategory,
  type RestaurantCategory,
  type PreferencesInput,
} from "$eave-dashboard/js/graphql/generated/graphql"

import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Paper from "$eave-dashboard/js/components/Paper";
import { RestaurantCategorySelections, ActivityCategorySelections } from "$eave-dashboard/js/components/Selections/CategorySelections";

const ViewContainer = styled("div")(() => ({
  padding: "24px 16px",
}));

const Title = styled(Typography)(() => ({
  marginBottom: 16,
}));

const PreferenceCount = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("12px"),
  lineHeight: rem("18px"),
  textAlign: "right",
}));

const SkipButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontFamily: "inherit",
  position: "absolute",
  padding: "16px",
  fontWeight: 400,
  right: 0,
  top: 0,
  "&:hover": {
    backgroundColor: "transparent",
  }
}));

const ProgressBar = styled(LinearProgress)(({ theme }) => ({
  backgroundColor: theme.palette.text.primary,
  height: 8,
  borderRadius: "10px",
  margin: "12px 0 4px",
}));

interface PreferencesViewProps {
  title: string;
  subtitle: string;
  userPreferences?: PreferencesInput|null,
  onSubmitOpenToBars: (open: boolean) => void;
  onSubmitRestaurants: (categories: RestaurantCategory[]) => void;
  onSubmitActivities: (categories: ActivityCategory[]) => void;
  onSkip: () => void;
}

const PreferencesView = ({
  title,
  subtitle,
  userPreferences,
  onSubmitOpenToBars,
  onSubmitRestaurants,
  onSubmitActivities,
  onSkip,
}: PreferencesViewProps) => {
  const {
    data: activityCategoriesData,
    isLoading: activityCategoriesAreLoading,
  } = useGetActivityCategoriesQuery({});
  const {
    data: restaurantCategoriesData,
    isLoading: restaurantCategoriesAreLoading,
  } = useGetRestaurantCategoriesQuery({});
  const [stepsCompleted, setStepsCompleted] = useState(0);

  // TODO: update query once backend is merged.
  const allActivityCategories = activityCategoriesData?.activityCategories || [];
  const allRestaurantCategories = restaurantCategoriesData?.restaurantCategories || [];
  const progress = (stepsCompleted / 8) * 100;

  // TODO remove.
  const TEMPselectedRestaurantCategories = allRestaurantCategories?.filter((x, i) => i % 2 == 0);
  const TEMPselectedActivityCategories = allActivityCategories?.filter((x, i) => i % 2 == 0);

  // TODO: Loading state. (use basic version of loading view)
  if (activityCategoriesAreLoading || restaurantCategoriesAreLoading) {
    return (
      <ViewContainer>

      </ViewContainer>
    )
  }


  return (
    <ViewContainer>
      <Paper>
        <SkipButton onClick={onSkip}>Skip all</SkipButton>
        <Title variant="h3">{title}</Title>
        <Typography variant="subtitle1">{subtitle}</Typography>
        <ProgressBar variant="determinate" value={progress} />
        <PreferenceCount>{stepsCompleted}/8 preferences</PreferenceCount>
      </Paper>
      <RestaurantCategorySelections
          categoryGroupName="Food types"
          allCategories={allRestaurantCategories}
          selectedCategories={TEMPselectedRestaurantCategories}
          accentColor={colors.lightOrangeAccent}
          onSubmit={onSubmitRestaurants}
          // collapsed={false}
          // collapsable
      />
    </ViewContainer>
  );
};

export default PreferencesView;
