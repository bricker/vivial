import React from "react";

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
}

const GlossaryIcon: React.FC<LogoIconProps> = ({ color = "black", width = "24px", height = "24px" }) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ minWidth: width, minHeight: height }}
    >
      <path d="M6.375 5.625L9.375 5.625" stroke="#7D7D7D" stroke-width="1.5" stroke-linecap="round" />
      <path d="M6.375 11.625L8.625 11.625" stroke="#7D7D7D" stroke-width="1.5" stroke-linecap="round" />
      <path d="M6.375 8.625L10.875 8.625" stroke="#7D7D7D" stroke-width="1.5" stroke-linecap="round" />
      <circle cx="13.875" cy="14.25" r="1.875" stroke="#7D7D7D" stroke-width="1.5" />
      <path d="M16.5 16.875L15.375 15.75" stroke="#7D7D7D" stroke-width="1.5" stroke-linecap="round" />
      <path
        d="M14.25 9.375L14.25 6.5625C14.25 3.91601 14.25 2.59277 13.4729 1.73532C13.4069 1.66257 13.3374 1.59309 13.2647 1.52715C12.4072 0.75 11.084 0.75 8.4375 0.75V0.75C5.79102 0.75 4.46777 0.75 3.61032 1.52715C3.53757 1.59309 3.46809 1.66257 3.40215 1.73532C2.625 2.59277 2.625 3.91601 2.625 6.5625V11.25C2.625 14.0784 2.625 15.4926 3.50368 16.3713C4.38236 17.25 5.79657 17.25 8.625 17.25H9.75"
        stroke="#7D7D7D"
        stroke-width="1.5"
        stroke-linecap="round"
      />
    </svg>
  );
};

export default GlossaryIcon;
