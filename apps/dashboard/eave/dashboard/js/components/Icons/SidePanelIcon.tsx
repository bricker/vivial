import React from "react";

const SidePanelIcon = (
  { color = "black" }: { color?: string; }
) => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M3.5 5.5L3.5 18.5C3.5 19.6046 4.39543 20.5 5.5 20.5L18.5 20.5C19.6046 20.5 20.5 19.6046 20.5 18.5L20.5 5.5C20.5 4.39543 19.6046 3.5 18.5 3.5L5.5 3.5C4.39543 3.5 3.5 4.39543 3.5 5.5Z"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path d="M15.5 20.5L15.5 3.5" stroke={color} strokeLinecap="round" />
      <path
        d="M10.5 14.5L12.5 12M12.5 12L10.5 9.5M12.5 12L7 12"
        stroke={color}
      />
    </svg>
  );
};

export default SidePanelIcon;
