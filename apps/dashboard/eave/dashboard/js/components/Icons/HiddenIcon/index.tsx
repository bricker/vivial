import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const HiddenIcon = ({ width = 24, height = 24, color = colors.midGreySecondaryField }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path
        d="M20 14.8335C21.3082 13.3317 22 12 22 12C22 12 18.3636 5 12 5C11.6588 5 11.3254 5.02013 11 5.05822C10.6578 5.09828 10.3244 5.15822 10 5.23552M3 3L6.71862 6.71862M6.71862 6.71862C3.66692 8.79117 2 12 2 12C2 12 5.63636 19 12 19C14.0551 19 15.8258 18.2699 17.2814 17.2814M6.71862 6.71862L9.87868 9.87868M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213M9.87868 9.87868L14.1213 14.1213M14.1213 14.1213L17.2814 17.2814M17.2814 17.2814L21 21"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default HiddenIcon;
