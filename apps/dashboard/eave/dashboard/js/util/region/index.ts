import { type Outing } from "$eave-dashboard/js/graphql/generated/graphql";
import { imageUrl } from "../asset";
import { REGION_IMAGE_PATHS, REGION_LABELS } from "./constant";

export function getRegionLabel(regionId: string): string | undefined {
  return REGION_LABELS[regionId];
}

export function getRegionImage(regionId: string | undefined): string | undefined {
  const imgPath = (regionId && REGION_IMAGE_PATHS[regionId]) || "regions/dtla.png";
  return imageUrl(imgPath);
}

export function getRegionIds(outing: Outing | null): string[] {
  const restaurantRegionId = outing?.restaurantRegion?.id;
  const activityRegionId = outing?.activityRegion?.id;
  const ids: string[] = [];
  if (restaurantRegionId) {
    ids.push(restaurantRegionId);
  }
  if (activityRegionId && activityRegionId !== restaurantRegionId) {
    ids.push(activityRegionId);
  }
  return ids;
}

export function getMultiRegionLabel(regionIds: string[]): string {
  let label = "";
  regionIds.forEach((id, i) => {
    label += getRegionLabel(id);
    if (i !== regionIds.length - 1) {
      label += ", ";
    }
  });
  return label;
}
