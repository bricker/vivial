import React from "react";
import { colors } from "../../../theme/colors";
import { IconProps } from "../types";

const CloseIcon = ({ width = 24, height = 24, color = colors.vivialYellow }: IconProps) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M22.3333 1L1 22.3333M22.3333 22.3333L1 1" stroke={color} strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
};

export default CloseIcon;
