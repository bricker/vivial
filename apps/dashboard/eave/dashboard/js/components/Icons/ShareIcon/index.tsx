import React from "react";
import { IconProps } from "../types";

const ShareIcon = (props: IconProps) => {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1.5" y="7.5" width="15" height="10" rx="1.5" fill="black" stroke={props.color} />
      <rect x="6" y="4" width="6" height="5" rx="1" fill="black" />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M9 0.75C9.13261 0.75 9.25979 0.802678 9.35355 0.896447L13.1036 4.64645C13.2988 4.84171 13.2988 5.15829 13.1036 5.35355C12.9083 5.54882 12.5917 5.54882 12.3964 5.35355L9.5 2.45711L9.5 12C9.5 12.2761 9.27614 12.5 9 12.5C8.72386 12.5 8.5 12.2761 8.5 12L8.5 2.45711L5.60355 5.35355C5.40829 5.54882 5.09171 5.54882 4.89645 5.35355C4.70118 5.15829 4.70118 4.84171 4.89645 4.64645L8.64645 0.896447C8.74021 0.802678 8.86739 0.75 9 0.75Z"
        fill={props.color}
      />
    </svg>
  );
};

export default ShareIcon;
