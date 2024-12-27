import React from "react";
import { colors } from "../../../theme/colors";
import { IconProps } from "../types";

const CalendarCheckIcon = ({ width = 42, height = 42, color = colors.pureWhite }: IconProps) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M9.625 15.5999H34.125M12.7917 5.25V7.95032M30.625 5.25V7.94999M30.625 7.94999H13.125C10.2255 7.94999 7.875 10.3676 7.875 13.35V31.35C7.875 34.3323 10.2255 36.75 13.125 36.75H30.625C33.5245 36.75 35.875 34.3323 35.875 31.35L35.875 13.35C35.875 10.3676 33.5245 7.94999 30.625 7.94999ZM17.5 26.4L20.125 29.1L26.25 22.8"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default CalendarCheckIcon;
