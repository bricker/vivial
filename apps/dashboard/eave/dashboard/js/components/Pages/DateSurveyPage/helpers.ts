import {
  type ActivityCategoryGroup,
  type OutingPreferences,
  type OutingPreferencesInput,
  type RestaurantCategory,
} from "$eave-dashboard/js/graphql/generated/graphql";

/**
 * If it's before 6:00 PM at the time that this function is called,
 * this function returns 6:00 PM the next day.
 *
 * Otherwise, this function returns 6:00 PM two days from the currrent day.
 */
export function getInitialStartTime(): Date {
  const now = new Date();
  const startTime = new Date(now);
  const sixPM = 18;
  startTime.setHours(sixPM, 0, 0);
  if (now.getHours() < sixPM) {
    startTime.setDate(now.getDate() + 1);
  } else {
    startTime.setDate(now.getDate() + 2);
  }
  return startTime;
}

export function getHoursDiff(date1: Date, date2: Date): number {
  const msDiff = Math.abs(date1.getTime() - date2.getTime());
  return msDiff / (1000 * 60 * 60);
}

export function in24Hours(): Date {
  const now = new Date();
  const millisecondsIn24Hours = 24 * 60 * 60 * 1000;
  return new Date(now.getTime() + millisecondsIn24Hours);
}

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
