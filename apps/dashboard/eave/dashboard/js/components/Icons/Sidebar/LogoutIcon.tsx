import React from "react";

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
}

const LogoutIcon: React.FC<LogoIconProps> = ({ color = "black", width = "24px", height = "24px" }) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ minWidth: width, minHeight: height }}
    >
      <g clip-path="url(#clip0_179_3025)">
        <path
          d="M12.2143 13.5V16.0714C12.2143 16.4124 12.0788 16.7395 11.8377 16.9805C11.5966 17.2216 11.2695 17.3571 10.9285 17.3571H1.92854C1.58754 17.3571 1.26052 17.2216 1.0194 16.9805C0.778281 16.7395 0.642822 16.4124 0.642822 16.0714V1.92854C0.642822 1.58754 0.778281 1.26052 1.0194 1.0194C1.26052 0.778281 1.58754 0.642822 1.92854 0.642822H10.9285C11.2695 0.642822 11.5966 0.778281 11.8377 1.0194C12.0788 1.26052 12.2143 1.58754 12.2143 1.92854V4.49997"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M8.35718 9H17.3572"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M14.7856 6.42859L17.3571 9.00002L14.7856 11.5714"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </g>
      <defs>
        <clipPath id="clip0_179_3025">
          <rect width="18" height="18" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};

export default LogoutIcon;
