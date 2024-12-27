import React from "react";
import { colors } from "../../../theme/colors";
import { IconProps } from "../types";

const MenuIcon = ({ width = 28, height = 21, color = colors.vivialYellow }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path
        d="M26.7302 8.96902H1.26985C0.56853 8.96902 0 9.53756 0 10.2389C0 10.9402 0.568529 11.5087 1.26985 11.5087H26.7302C27.4315 11.5087 28 10.9402 28 10.2389C28 9.53756 27.4315 8.96902 26.7302 8.96902Z"
        fill={color}
      />
      <path
        d="M26.7302 0.0797424H1.26984C0.568526 0.0797424 0 0.648269 0 1.34958C0 2.05089 0.568526 2.61942 1.26984 2.61942H26.7302C27.4315 2.61942 28 2.05089 28 1.34958C28 0.648269 27.4315 0.0797424 26.7302 0.0797424Z"
        fill={color}
      />
      <path
        d="M26.7302 17.8571H1.26985C0.56853 17.8571 0 18.4257 0 19.127C0 19.8283 0.568529 20.3968 1.26985 20.3968H26.7302C27.4315 20.3968 28 19.8283 28 19.127C28 18.4257 27.4315 17.8571 26.7302 17.8571Z"
        fill={color}
      />
    </svg>
  );
};

export default MenuIcon;
