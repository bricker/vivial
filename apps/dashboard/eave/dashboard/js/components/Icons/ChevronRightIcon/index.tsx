import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const ChevronRightIcon = ({ width = 28, height = 28, color = colors.whiteText }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg width={height} height={width} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 6L18 14L10 22" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default ChevronRightIcon;
