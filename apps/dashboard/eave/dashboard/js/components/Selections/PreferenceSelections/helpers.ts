import { type ActivityCategoryGroup } from "$eave-dashboard/js/graphql/generated/graphql";
import { colors } from "$eave-dashboard/js/theme/colors";
import { type Category } from "$eave-dashboard/js/types/category";
import { CATEGORY_ACCENT_COLOR_MAP } from "./constants";

export function getCategoryMap(categoryList: Category[]): { [key: string]: string } {
  const map: { [key: string]: string } = {};
  categoryList.forEach((category) => {
    map[category.id] = category.name;
  });
  return map;
}

export function getAccentColor(categoryId?: string): string {
  if (categoryId) {
    const accentColor = CATEGORY_ACCENT_COLOR_MAP[categoryId];
    if (accentColor) {
      return accentColor;
    }
  }
  return colors.lightOrangeAccent;
}

export function getDefaults({
  preferredCategories,
  allCategories,
}: {
  preferredCategories: Category[];
  allCategories: Category[];
}): Category[] {
  if (preferredCategories.length) {
    return preferredCategories;
  } else {
    return allCategories.filter((category) => category.isDefault);
  }
}

export function initCollapsedGroups(groups: ActivityCategoryGroup[]): Map<string, boolean> {
  const map: Map<string, boolean> = new Map();
  map.set("default", true);
  groups.forEach((group) => map.set(group.id, false));
  return map;
}
