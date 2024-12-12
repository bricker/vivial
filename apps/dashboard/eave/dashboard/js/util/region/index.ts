import { REGION_LABELS } from "./constant";

export function getRegionLabel(regionId: string): string | undefined {
  return REGION_LABELS[regionId];
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
