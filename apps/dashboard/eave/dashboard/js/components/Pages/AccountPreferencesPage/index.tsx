import { type OutingPreferencesFieldsFragment } from "$eave-dashboard/js/graphql/generated/graphql";
import { type Category } from "$eave-dashboard/js/types/category";
import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";

import {
  useGetOutingPreferencesQuery,
  useUpdateOutingPreferencesMutation,
} from "$eave-dashboard/js/store/slices/coreApiSlice";
import { getDefaults, initCollapsedGroups } from "../../Selections/PreferenceSelections/helpers";

import Typography from "@mui/material/Typography";
import BackButton from "../../Buttons/BackButton";
import Paper from "../../Paper";
import PreferenceSelections from "../../Selections/PreferenceSelections";
import LoadingView from "./LoadingView";

const PageContainer = styled("div")(() => ({
  padding: "12px 16px 102px",
  maxWidth: 600,
  margin: "0 auto",
}));

const CopyContainer = styled(Paper)(() => ({
  padding: "24px 40px",
  margin: "12px 0px 16px",
}));

const Subtitle = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  marginTop: 16,
}));

const AccountPreferencesPage = () => {
  const { data, isLoading } = useGetOutingPreferencesQuery({});
  const [updatePreferences] = useUpdateOutingPreferencesMutation();
  const [outingPreferences, setOutingPreferences] = useState<OutingPreferencesFieldsFragment | null>(null);
  const [collapsedGroups, setCollapsedGroups] = useState<Map<string, boolean>>(new Map());
  const restaurantCategories = data?.restaurantCategories || [];
  const activityCategoryGroups = data?.activityCategoryGroups || [];

  const handleCollapse = useCallback(() => {
    const newCollapsedGroups = new Map(collapsedGroups);
    let collapse = false;
    for (const id of newCollapsedGroups.keys()) {
      if (collapse) {
        newCollapsedGroups.set(id, true);
        setCollapsedGroups(newCollapsedGroups);
        return;
      }
      if (newCollapsedGroups.get(id)) {
        newCollapsedGroups.set(id, false);
        collapse = true;
      }
    }
    newCollapsedGroups.set("default", true);
    setCollapsedGroups(newCollapsedGroups);
  }, [collapsedGroups]);

  const handleSubmitRestaurants = useCallback(async (selectedCategories: Category[]) => {
    const restaurantCategoryIds = selectedCategories.map((c) => c.id);
    const resp = await updatePreferences({ input: { restaurantCategoryIds } });
    const viewer = resp.data?.viewer;
    if (
      viewer?.__typename === "AuthenticatedViewerMutations" &&
      viewer.updatePreferences.__typename === "UpdateOutingPreferencesSuccess"
    ) {
      setOutingPreferences(viewer.updatePreferences.outingPreferences);
    }
  }, []);

  const handleSubmitActivities = useCallback(
    async (selectedCategories: Category[], removedCategories?: Category[]) => {
      let activityCategoryIds = outingPreferences?.activityCategories?.map((c) => c.id) || [];
      if (removedCategories) {
        const removedCategoryIds = removedCategories.map((c) => c.id);
        activityCategoryIds = activityCategoryIds.filter((id) => !removedCategoryIds.includes(id));
      }
      selectedCategories.forEach((c) => {
        if (!activityCategoryIds.includes(c.id)) {
          activityCategoryIds.push(c.id);
        }
      });
      const resp = await updatePreferences({ input: { activityCategoryIds } });
      const viewer = resp.data?.viewer;
      if (
        viewer?.__typename === "AuthenticatedViewerMutations" &&
        viewer.updatePreferences.__typename === "UpdateOutingPreferencesSuccess"
      ) {
        setOutingPreferences(viewer.updatePreferences.outingPreferences);
      }
    },
    [outingPreferences],
  );

  useEffect(() => {
    const viewer = data?.viewer;
    if (viewer?.__typename === "AuthenticatedViewerQueries") {
      setOutingPreferences(viewer.outingPreferences);
    }
    if (data?.activityCategoryGroups) {
      setCollapsedGroups(initCollapsedGroups(data.activityCategoryGroups));
    }
  }, [data]);

  if (isLoading || outingPreferences === null) {
    return <LoadingView />;
  }

  return (
    <PageContainer>
      <BackButton />
      <CopyContainer>
        <Typography variant="h3">Preferences</Typography>
        <Subtitle variant="subtitle1">
          Your saved preferences are used to make more personalized recommendations.
        </Subtitle>
      </CopyContainer>
      <PreferenceSelections
        categoryGroupName="Food types"
        categories={restaurantCategories}
        defaultCategories={getDefaults({
          preferredCategories: outingPreferences?.restaurantCategories || [],
          allCategories: restaurantCategories,
        })}
        onSubmit={handleSubmitRestaurants}
        onCollapse={handleCollapse}
        collapsed={collapsedGroups.get("default")}
        collapsable
      />
      {activityCategoryGroups?.map((group) => (
        <PreferenceSelections
          key={group.id}
          categoryGroupName={group.name}
          categoryGroupId={group.id}
          categories={group.activityCategories || []}
          defaultCategories={getDefaults({
            preferredCategories: outingPreferences?.activityCategories || [],
            allCategories: group.activityCategories,
          })}
          onSubmit={handleSubmitActivities}
          onCollapse={handleCollapse}
          collapsed={collapsedGroups.get(group.id)}
          collapsable
        />
      ))}
    </PageContainer>
  );
};

export default AccountPreferencesPage;
