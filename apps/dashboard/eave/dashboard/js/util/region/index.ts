import { imageUrl } from "../asset";
import { REGION_IMAGE_PATHS, REGION_LABELS } from "./constant";

export function getRegionLabel(regionId: string): string | undefined {
  return REGION_LABELS[regionId];
}

export function getRegionImage(regionId: string | undefined): string | undefined {
  const imgPath = (regionId && REGION_IMAGE_PATHS[regionId]) || "regions/dtla.png";
  return imageUrl(imgPath);
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
