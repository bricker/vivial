import React, { useState, useCallback } from "react";
import { useGetOutingPreferencesQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { type OutingPreferences } from "$eave-dashboard/js/graphql/generated/graphql"
import { type Category } from "$eave-dashboard/js/types/category";

import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import Paper from "$eave-dashboard/js/components/Paper";
import PreferenceSelections from "$eave-dashboard/js/components/Selections/PreferenceSelections";
import LoadingView from "../LoadingView";

import { getDefaults } from "./helpers";

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
  onSubmitRestaurants: (categories: Category[]) => void;
  onSubmitActivities: (categories: Category[]) => void;
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
  const { data, isLoading } = useGetOutingPreferencesQuery({});
  const [stepsCompleted, setStepsCompleted] = useState(0);
  const restaurantCategories = data?.restaurantCategories || [];
  const activityCategoryGroups = data?.activityCategoryGroups || [];
  const preferredRestaurants = outingPreferences?.restaurantCategories || [];
  const preferredActivities = outingPreferences?.activityCategories || [];
  const progress = (stepsCompleted / 8) * 100;

  if (isLoading) {
    return <LoadingView />
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
      <PreferenceSelections
        categoryGroupName="Food types"
        categories={restaurantCategories}
        defaultCategories={getDefaults(preferredRestaurants, restaurantCategories)}
        onSubmit={onSubmitRestaurants}
      />
      {activityCategoryGroups?.map(group => (
          <PreferenceSelections key={group.id}
            categoryGroupName={group.name}
            categoryGroupId={group.id}
            categories={group?.activityCategories || []}
            defaultCategories={getDefaults(preferredActivities, group?.activityCategories)}
            onSubmit={onSubmitActivities}
        />
      ))}
    </ViewContainer>
  );
};

export default PreferencesView;
