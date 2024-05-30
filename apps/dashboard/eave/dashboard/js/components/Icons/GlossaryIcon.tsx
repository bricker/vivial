import React from "react";

const GlossaryIcon = ({ color = "black" }: { color?: string }) => {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 14L26 14" stroke={color} strokeWidth="4" strokeLinecap="round" />
      <path d="M18 30L24 30" stroke={color} strokeWidth="4" strokeLinecap="round" />
      <path d="M18 22L30 22" stroke={color} strokeWidth="4" strokeLinecap="round" />
      <path
        d="M38 22V12C38 9.17157 38 7.75736 37.1213 6.87868C36.2426 6 34.8284 6 32 6H16C13.1716 6 11.7574 6 10.8787 6.87868C10 7.75736 10 9.17157 10 12V36C10 38.8284 10 40.2426 10.8787 41.1213C11.7574 42 13.1716 42 16 42H24"
        stroke={color}
        strokeWidth="4"
      />
      <circle cx="35" cy="35" r="5" stroke={color} strokeWidth="3" />
      <path d="M42 42L39 39" stroke={color} strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
};

export default GlossaryIcon;
