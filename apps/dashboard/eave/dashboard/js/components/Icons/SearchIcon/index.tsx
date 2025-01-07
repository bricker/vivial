import { colors } from "$eave-dashboard/js/theme/colors";
import React from "react";

const SearchIcon = ({ color = colors.whiteText }: { color?: string }) => {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M18.9572 21.0785L13.2519 15.3732L15.3732 13.2518L21.0786 18.9572C21.6644 19.543 21.6644 20.4927 21.0786 21.0785C20.4928 21.6643 19.543 21.6643 18.9572 21.0785Z"
        fill={color}
      />
      <circle cx="8.60716" cy="8.60716" r="7.60716" stroke={color} strokeWidth="2" />
    </svg>
  );
};

export default SearchIcon;
