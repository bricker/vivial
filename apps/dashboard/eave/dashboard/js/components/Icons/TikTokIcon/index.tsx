import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const TikTokIcon = ({ width = 12, height = 14, color = colors.whiteText }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path
        fill={color}
        d="M8.81129 0.977445L8.48037 0.481506H6.47777V4.9482L6.47094 9.31116C6.47436 9.34358 6.47777 9.37924 6.47777 9.41165C6.47777 10.504 5.54299 11.3954 4.38988 11.3954C3.23676 11.3954 2.30199 10.5073 2.30199 9.41165C2.30199 8.31929 3.23676 7.42789 4.38988 7.42789C4.62869 7.42789 4.86068 7.47003 5.07561 7.54134V5.3631C4.85385 5.32745 4.62528 5.308 4.38988 5.308C2.012 5.31124 0.0742188 7.15237 0.0742188 9.41489C0.0742188 11.6774 2.012 13.5185 4.39329 13.5185C6.77458 13.5185 8.71236 11.6774 8.71236 9.41489V4.22536C9.57549 5.04544 10.6911 5.84608 11.9261 6.10215V3.87528C10.5853 3.31128 9.25139 1.64518 8.81129 0.977445Z"
      />
    </svg>
  );
};

export default TikTokIcon;
