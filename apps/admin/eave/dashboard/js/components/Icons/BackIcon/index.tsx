import React from "react";
import { colors } from "../../../theme/colors";

interface BackIconProps {
  color?: string;
  large?: boolean;
}

const BackIcon = ({ color = colors.pureWhite, large }: BackIconProps) => {
  if (large) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
        <path d="M20 24L12 16L20 8" stroke={color} strokeWidth="2.22249" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M14 17L9 12L14 7" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default BackIcon;
