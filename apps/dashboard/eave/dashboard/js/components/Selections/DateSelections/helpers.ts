import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";

export function getSearchAreaLabel(searchAreaIds: string[], searchRegions: SearchRegion[]): string {
  if (searchAreaIds.length === searchRegions.length) {
    return "Anywhere in LA";
  }
  const regionMap: { [key: string]: string } = {};
  let label = "";
  searchRegions.forEach((region) => (regionMap[region.id] = region.name));
  searchAreaIds.forEach((id, i) => {
    label += regionMap[id];
    if (i !== searchAreaIds.length - 1) {
      label += ", ";
    }
  });
  return label;
}
