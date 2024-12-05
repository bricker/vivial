import { type Category } from "$eave-dashboard/js/types/category";

export function getDefaults(preferredCategories: Category[], categoryOptions: Category[]): Category[] {
  if (preferredCategories?.length) {
    return preferredCategories;
  }
  if (categoryOptions?.length) {
    return categoryOptions.filter((category) => category.isDefault);
  }
  return [];
}
