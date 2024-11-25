import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";
import { IconProps } from "../types";

const CloseIcon = ({ width = 23, height = 21, color = colors.vivialYellow }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path
        d="M21.4725 17.9984L2.6488 0.85503C2.13029 0.38281 1.32715 0.420332 0.854931 0.938837C0.382711 1.45734 0.420233 2.26048 0.938738 2.7327L19.7625 19.8761C20.281 20.3483 21.0841 20.3108 21.5563 19.7923C22.0285 19.2738 21.991 18.4706 21.4725 17.9984Z"
        fill={color}
      />
      <path
        d="M21.4725 2.7327L2.6488 19.8761C2.13029 20.3483 1.32715 20.3108 0.854931 19.7923C0.382711 19.2738 0.420233 18.4706 0.938738 17.9984L19.7625 0.855021C20.281 0.382801 21.0841 0.420324 21.5563 0.938829C22.0285 1.45733 21.991 2.26048 21.4725 2.7327Z"
        fill={color}
      />
    </svg>
  );
};

export default CloseIcon;
