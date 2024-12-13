import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";

const SettingsIcon = ({ color = colors.whiteText }: { color?: string }) => {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28" fill="none">
      <path
        d="M3.5 9.33333L17.5 9.33333M17.5 9.33333C17.5 11.2663 19.067 12.8333 21 12.8333C22.933 12.8333 24.5 11.2663 24.5 9.33333C24.5 7.40033 22.933 5.83333 21 5.83333C19.067 5.83333 17.5 7.40033 17.5 9.33333ZM10.5 18.6667L24.5 18.6667M10.5 18.6667C10.5 20.5997 8.933 22.1667 7 22.1667C5.067 22.1667 3.5 20.5997 3.5 18.6667C3.5 16.7337 5.067 15.1667 7 15.1667C8.933 15.1667 10.5 16.7337 10.5 18.6667Z"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default SettingsIcon;
