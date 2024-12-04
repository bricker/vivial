import {
  type ActivitySubcategory,
  type RestaurantCategory
} from "$eave-dashboard/js/graphql/generated/graphql"

// TODO: this will look different post backend changes.
// TODO: move to types.
type Category = ActivitySubcategory | RestaurantCategory;

export function getSelectedCategoryIds(allCategories: Category[], selectedCategories: Category[]): string[] {
  if (selectedCategories?.length) {
    return selectedCategories.map(category => category.id);
  }
  // TODO: uncoment once backend is merged.
  // const defaultCategories = allCategories.filter(category => category.isDefault);
  // return defaultCategories.map(category => category.id);
  return allCategories.map(category => category.id);
}

export function getCategoryMap(categoryList: Category[]): {[key: string]: string} {
  const map: {[key: string]: string} = {}
  categoryList.forEach(category => {
    map[category.id] = category.name;
  });
  return map;
}
