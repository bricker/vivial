import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const BackIcon = ({ width = 24, height = 24, color = colors.whiteText }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path d="M14 17L9 12L14 7" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default BackIcon;
