import { type Category } from "$eave-dashboard/js/types/category";
import { colors } from "$eave-dashboard/js/theme/colors";
import { CATEGORY_ACCENT_COLOR_MAP } from "./constants";

export function getCategoryMap(categoryList: Category[]): {[key: string]: string} {
  const map: {[key: string]: string} = {}
  categoryList.forEach(category => {
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
