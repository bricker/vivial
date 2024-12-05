import React, { useState, useCallback } from "react";
import { useGetOutingPreferencesQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { colors } from "$eave-dashboard/js/theme/colors";
import {
  type ActivityCategory,
  type RestaurantCategory,
  type OutingPreferences,
} from "$eave-dashboard/js/graphql/generated/graphql"

import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Paper from "$eave-dashboard/js/components/Paper";
import { RestaurantPreferenceSelections } from "$eave-dashboard/js/components/Selections/PreferenceSelections";

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
  outingPreferences: OutingPreferences|null,
  onSubmitRestaurants: (categories: RestaurantCategory[]) => void;
  onSubmitActivities: (categories: ActivityCategory[]) => void;
  onSkip: () => void;
}

const PreferencesView = ({
  title,
  subtitle,
  outingPreferences,
  onSubmitRestaurants,
  onSubmitActivities,
  onSkip,
}: PreferencesViewProps) => {
  const { data } = useGetOutingPreferencesQuery({});
  const restaurantCategories = data?.restaurantCategories;
  const activityCategoryGroups = data?.activityCategoryGroups;
  const defaultRestaurantCategories = outingPreferences?.restaurantCategories || restaurantCategories?.filter(c => c.isDefault);

  const [stepsCompleted, setStepsCompleted] = useState(0);
  const progress = (stepsCompleted / 8) * 100;

  return (
    <ViewContainer>
      <Paper>
        <SkipButton onClick={onSkip}>Skip all</SkipButton>
        <Title variant="h3">{title}</Title>
        <Typography variant="subtitle1">{subtitle}</Typography>
        <ProgressBar variant="determinate" value={progress} />
        <PreferenceCount>{stepsCompleted}/8 preferences</PreferenceCount>
      </Paper>
      <RestaurantPreferenceSelections
        categoryGroupName="Food types"
        accentColor={colors.lightOrangeAccent}
        categories={restaurantCategories || []}
        defaultCategories={defaultRestaurantCategories || []}
        onSubmit={onSubmitRestaurants}
      />
    </ViewContainer>
  );
};

export default PreferencesView;
