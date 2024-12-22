import { type OutingPreferencesInput } from "$eave-dashboard/js/graphql/generated/graphql";
import type { OutingPreferencesSelections } from "../store/slices/outingSlice";

export function getPreferenceInputs(
  userPreferences: OutingPreferencesSelections | null,
  partnerPreferenecs: OutingPreferencesSelections | null,
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
  return [];
}
