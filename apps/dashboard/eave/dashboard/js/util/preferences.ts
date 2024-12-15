import {
  type ActivityCategoryGroup,
  type OutingPreferences,
  type OutingPreferencesInput,
  type RestaurantCategory,
} from "$eave-dashboard/js/graphql/generated/graphql";

export function getPreferenceInputs(
  userPreferences: OutingPreferences | null,
  partnerPreferenecs: OutingPreferences | null,
  activityGroups?: ActivityCategoryGroup[],
  restaurantCategories?: RestaurantCategory[],
): OutingPreferencesInput[] {
  const userPreferencesInput: OutingPreferencesInput = {
    activityCategoryIds: userPreferences?.activityCategories?.map((c) => c.id) || [],
    restaurantCategoryIds: userPreferences?.restaurantCategories?.map((c) => c.id) || [],
  };
  const partnerPreferenecsInput: OutingPreferencesInput = {
    activityCategoryIds: partnerPreferenecs?.activityCategories?.map((c) => c.id) || [],
    restaurantCategoryIds: partnerPreferenecs?.restaurantCategories?.map((c) => c.id) || [],
  };
  // Case 1: Both user and partner preferences are provided.
  if (userPreferences && partnerPreferenecs) {
    return [userPreferencesInput, partnerPreferenecsInput];
  }
  // Case 2: Only user preferenecs are provided.
  if (userPreferences) {
    return [userPreferencesInput];
  }
  // Case 3: Only partner preferences are provided (edge case).
  if (partnerPreferenecs) {
    return [partnerPreferenecsInput];
  }
  // Case 4: Preferences weren't provided, use defaults.
  if (activityGroups && restaurantCategories) {
    const defaultRestaurantCategoryIds: string[] = [];
    const defaultActivityCategoryIds: string[] = [];
    restaurantCategories.forEach((c) => {
      if (c.isDefault) {
        defaultRestaurantCategoryIds.push(c.id);
      }
    });
    activityGroups.forEach((group) => {
      group.activityCategories.forEach((c) => {
        if (c.isDefault) {
          defaultActivityCategoryIds.push(c.id);
        }
      });
    });
    const defaultPreferences: OutingPreferencesInput = {
      activityCategoryIds: defaultActivityCategoryIds,
      restaurantCategoryIds: defaultRestaurantCategoryIds,
    };
    return [defaultPreferences];
  }
  // Case 5: Defaults weren't provided.
  return [];
}
