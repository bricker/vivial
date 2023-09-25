import React from "react";

const CheckIcon = ({ circleColor, checkColor, className }) => {
  return (
    <svg className={className} fill="none" height="27" viewBox="0 0 28 27" width="28" xmlns="http://www.w3.org/2000/svg">
      <ellipse fill={circleColor || "#f4e346"} cx="14.2516" cy="13.5" rx="13.7163" ry="13.5"/>
      <path stroke={checkColor || "#121212"} d="m7.69168 14.9254 3.32992 2.458c.4263.3148 1.0241.2423 1.3629-.1652l8.5976-10.34247" strokeLinecap="round"/>
    </svg>
  );
};

export default CheckIcon;
