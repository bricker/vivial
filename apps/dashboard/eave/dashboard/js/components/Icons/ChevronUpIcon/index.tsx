import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

interface ChevronUpIconProps extends IconProps {
  large?: boolean;
}

const ChevronUpIcon = ({ color = colors.whiteText, large = false }: ChevronUpIconProps) => {
  if (large) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="16" viewBox="0 0 18 16" fill="none">
        <path d="M1 12L9 4L17 12" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M12 10L8 6L4 10" stroke={color} strokeWidth="2.15949" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default ChevronUpIcon;
