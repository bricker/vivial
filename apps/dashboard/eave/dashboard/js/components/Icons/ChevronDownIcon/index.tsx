import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const ChevronDownIcon = ({ color = colors.whiteText }: IconProps) => {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M12 6L8 10L4 6" stroke={color} strokeWidth="2.15949" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default ChevronDownIcon;
