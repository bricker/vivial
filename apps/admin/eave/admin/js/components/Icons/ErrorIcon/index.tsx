import React from "react";
import { colors } from "../../../theme/colors";
import { IconProps } from "../types";

const ErrorIcon = ({ size = 16, color = colors.errorRed }: IconProps) => {
  if (![16, 20].includes(size)) {
    return "Invalid Size";
  }
  const viewBox = `0 0 ${size} ${size}`;
  const r = size / 2;
  const d = size === 16 ? "M12 4L4 12M12 12L4 4" : "M16 4L4 16M16 16L4 4";
  return (
    <svg width={size} height={size} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx={r} cy={r} r={r} fill={color} />
      <path d={d} stroke="white" strokeLinecap="round" />
    </svg>
  );
};

export default ErrorIcon;
