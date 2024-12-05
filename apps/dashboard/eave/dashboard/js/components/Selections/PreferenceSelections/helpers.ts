import { type Category } from "$eave-dashboard/js/types/category";

export function getCategoryMap(categoryList: Category[]): {[key: string]: string} {
  const map: {[key: string]: string} = {}
  categoryList.forEach(category => {
    map[category.id] = category.name;
  });
  return map;
}
