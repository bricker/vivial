import {
  type ActivityCategoryFieldsFragment,
  type RestaurantCategoryFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";
import { useGetOutingPreferencesQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";

import { getDefaults } from "$eave-dashboard/js/components/Selections/PreferenceSelections/helpers";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { type Category } from "$eave-dashboard/js/types/category";
import { styled } from "@mui/material";
import React, { useState } from "react";

import Paper from "$eave-dashboard/js/components/Paper";
import PreferenceSelections from "$eave-dashboard/js/components/Selections/PreferenceSelections";
import type { OutingPreferencesSelections } from "$eave-dashboard/js/store/slices/outingSlice";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import LoadingView from "../LoadingView";

const ViewContainer = styled("div")(() => ({
  padding: "24px 16px 102px",
  maxWidth: 600,
  margin: "0 auto",
  overflow: "hidden",
}));

const SelectionsContainer = styled("div")(() => ({
  display: "flex",
  position: "relative",
  left: 0,
  marginTop: 16,
  "& div": {
    minWidth: "100%",
    marginRight: 16,
  },
}));

const Title = styled(Typography)(() => ({
  marginBottom: 16,
}));

const PreferenceCount = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem(12),
  lineHeight: rem(18),
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
  },
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
  outingPreferences: OutingPreferencesSelections | null;
  onSubmit: (selections: OutingPreferencesSelections) => void;
  onClose: () => void;
}

const PreferencesView = ({ title, subtitle, outingPreferences, onSubmit, onClose }: PreferencesViewProps) => {
  const { data, isLoading } = useGetOutingPreferencesQuery({});
  const [stepsCompleted, setStepsCompleted] = useState(0);
  const [selectedResaturantCategories, setSelectedResaturantCategories] = useState<RestaurantCategoryFieldsFragment[]>(
    [],
  );
  const [selectedActivityCategories, setSelectedActivityCategories] = useState<ActivityCategoryFieldsFragment[]>([]);
  const restaurantCategories = data?.restaurantCategories || [];
  const activityCategoryGroups = data?.activityCategoryGroups || [];
  const preferredRestaurants = outingPreferences?.restaurantCategories || [];
  const preferredActivities = outingPreferences?.activityCategories || [];
  const totalSteps = 8;
  const progress = (stepsCompleted / totalSteps) * 100;

  const animateSelectionsContainer = () => {
    const selectionsContainer = document.getElementById("selections-container");
    if (selectionsContainer) {
      const childWidth = selectionsContainer?.firstElementChild?.clientWidth || 0;
      const left = window.getComputedStyle(selectionsContainer).left;
      const newLeft = `${parseInt(left, 10) - childWidth - 16}px`; // 16px margin
      const keyframes = [{ left }, { left: newLeft }];
      selectionsContainer.animate(keyframes, {
        duration: 400,
        easing: "ease-out",
        fill: "forwards",
      });
    }
  };

  const handleStep = (stepNumber: number, selections: OutingPreferencesSelections) => {
    setStepsCompleted(stepNumber);
    if (stepNumber === totalSteps) {
      onSubmit(selections);
      onClose();
    } else {
      animateSelectionsContainer();
    }
  };

  const handleSubmitRestaurants = (categories: Category[]) => {
    const restaurantSelections = selectedResaturantCategories.concat(categories as RestaurantCategoryFieldsFragment[]);
    setSelectedResaturantCategories(restaurantSelections);
    handleStep(stepsCompleted + 1, {
      restaurantCategories: restaurantSelections,
      activityCategories: selectedActivityCategories,
    });
  };

  const handleSubmitActivities = (categories: Category[]) => {
    const activitySelections = selectedActivityCategories.concat(categories as ActivityCategoryFieldsFragment[]);
    setSelectedActivityCategories(activitySelections);
    handleStep(stepsCompleted + 1, {
      restaurantCategories: selectedResaturantCategories,
      activityCategories: activitySelections,
    });
  };

  if (isLoading) {
    return <LoadingView />;
  }

  return (
    <ViewContainer>
      <Paper>
        <SkipButton onClick={onClose}>Skip all</SkipButton>
        <Title variant="h3">{title}</Title>
        <Typography variant="subtitle1">{subtitle}</Typography>
        <ProgressBar variant="determinate" value={progress} />
        <PreferenceCount>{stepsCompleted}/8 preferences</PreferenceCount>
      </Paper>
      <SelectionsContainer id="selections-container">
        <PreferenceSelections
          categoryGroupName="Food types"
          categories={restaurantCategories}
          defaultCategories={getDefaults({
            preferredCategories: preferredRestaurants,
            allCategories: restaurantCategories,
          })}
          onSubmit={handleSubmitRestaurants}
        />
        {activityCategoryGroups?.map((group) => (
          <PreferenceSelections
            key={group.id}
            categoryGroupName={group.name}
            categoryGroupId={group.id}
            categories={group?.activityCategories || []}
            defaultCategories={getDefaults({
              preferredCategories: preferredActivities,
              allCategories: group?.activityCategories,
            })}
            onSubmit={handleSubmitActivities}
          />
        ))}
      </SelectionsContainer>
    </ViewContainer>
  );
};

export default PreferencesView;
