import {
  type ActivityCategory,
  type RestaurantCategory,
} from "$eave-dashboard/js/graphql/generated/graphql"

export function getCategoryMap(categoryList: RestaurantCategory[] | ActivityCategory[]): {[key: string]: string} {
  const map: {[key: string]: string} = {}
  categoryList.forEach(category => {
    map[category.id] = category.name;
  });
  return map;
}
