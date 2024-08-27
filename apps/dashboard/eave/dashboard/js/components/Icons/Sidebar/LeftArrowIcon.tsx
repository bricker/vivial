import { SidebarIcon } from "$eave-dashboard/js/theme";
import React from "react";

const LeftArrowIcon: React.FC<SidebarIcon> = ({ color = "black", width = "24px", height = "24px" }) => {
  return (
    <svg width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M15 6L9 12L15 18M15 12H15.01"
        stroke={color}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export default LeftArrowIcon;
