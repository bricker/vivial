import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const ErrorIcon = ({ size = 14, color = colors.errorRed }: IconProps) => {
  if (![14, 20].includes(size)) {
    return "Invalid Size";
  }
  const viewBox = `0 0 ${size} ${size}`;
  const r = size / 2;
  const d = size === 14 ? "M10.5 3.5L3.5 10.5M10.5 10.5L3.5 3.5" : "M16 4L4 16M16 16L4 4";
  return (
    <svg width={size} height={size} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx={r} cy={r} r={r} fill={color} />
      <path d={d} stroke="white" strokeLinecap="round" />
    </svg>
  );
};

export default ErrorIcon;
