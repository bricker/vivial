import { colors } from "$eave-admin/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

interface ChevronDownIconProps extends IconProps {
  large?: boolean;
  thin?: boolean;
}

const ChevronDownIcon = ({ color = colors.whiteText, large = false, thin = false }: ChevronDownIconProps) => {
  if (thin) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
        <path d="M12 6.26087L8 10.4348L4 6.26087" stroke={color} strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (large) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="16" viewBox="0 0 18 16" fill="none">
        <path d="M17 4L9 12L1 4" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M12 6L8 10L4 6" stroke={color} strokeWidth="2.15949" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export default ChevronDownIcon;
