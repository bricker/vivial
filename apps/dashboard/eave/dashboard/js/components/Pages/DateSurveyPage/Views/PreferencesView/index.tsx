import React from "react";
import {
  type ActivityCategory,
  type RestaurantCategory,
  type PreferencesInput,
} from "$eave-dashboard/js/graphql/generated/graphql"

interface PreferencesViewProps {
  title: string;
  subtitle: string;
  userPreferences?: PreferencesInput|null,
  onSubmitOpenToBars: (open: boolean) => void;
  onSubmitRestaurants: (categories: RestaurantCategory[]) => void;
  onSubmitActivities: (categories: ActivityCategory[]) => void;
}

const PreferencesView = ({
  title,
  subtitle,
  userPreferences,
  onSubmitOpenToBars,
  onSubmitRestaurants,
  onSubmitActivities,
}: PreferencesViewProps) => {
  return (
    <div>PREFERENCES VIEW</div>
  );
};

export default PreferencesView;
