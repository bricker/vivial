import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { imageUrl } from "../asset";
import { REGION_IMAGE_PATHS, REGION_LABELS } from "./constant";

export function getRegionLabel(regionId: string): string | undefined {
  return REGION_LABELS[regionId];
}

export function getRegionImage(regions: SearchRegion[]): string {
  const defaultImg = "regions/dtla.png";
  if (regions.length) {
    const regionId = regions[0]?.id;
    const regionImg = (regionId && REGION_IMAGE_PATHS[regionId]) || defaultImg;
    return imageUrl(regionImg);
  }
  return imageUrl(defaultImg);
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
