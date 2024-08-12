import React from "react";

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
}

const SetupIcon: React.FC<LogoIconProps> = ({ color = "black", width = "24px", height = "24px" }) => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ minWidth: width, minHeight: height }}
    >
      <g clip-path="url(#clip0_172_1724)">
        <path
          d="M0.642822 14.1001H17.3571"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M14.1428 17.3144L17.3571 14.1001L14.1428 10.8859"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M2.8287 7.42812V1.94202C2.8287 2.69948 2.21464 3.31353 1.45718 3.31353H1"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M4.65716 7.42822H0.999756"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M10.8285 7.42812H7.17114V6.64881C7.17114 6.1039 7.49372 5.61069 7.99293 5.39227L10.0281 4.5019C10.5143 4.28915 10.8285 3.80873 10.8285 3.27796C10.8285 2.54014 10.2304 1.94202 9.4926 1.94202H8.54267C7.94549 1.94202 7.43747 2.32367 7.24919 2.85637"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M15.6641 4.45667C16.4215 4.45667 17.0356 5.07072 17.0356 5.82819V6.05679C17.0356 6.81425 16.4215 7.42831 15.6641 7.42831L14.7497 7.42832C14.1525 7.42832 13.6445 7.04666 13.4563 6.51395"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M13.6543 2.85637C13.8036 2.32868 14.2887 1.94203 14.8642 1.94202H15.55C16.2444 1.942 16.8073 2.50489 16.8073 3.19925C16.8073 3.8936 16.2444 4.45649 15.55 4.45649L15.4357 4.45648"
          stroke="#147915"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </g>
      <defs>
        <clipPath id="clip0_172_1724">
          <rect width="18" height="18" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};

export default SetupIcon;
