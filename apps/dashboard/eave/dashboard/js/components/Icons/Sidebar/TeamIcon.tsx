import React from "react";

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
}

const TeamIcon: React.FC<LogoIconProps> = ({ color = "black", width = "24px", height = "24px" }) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ minWidth: width, minHeight: height }}
    >
      <g clip-path="url(#clip0_177_2929)">
        <path
          d="M6.42864 8.85716C8.20384 8.85716 9.64293 7.41807 9.64293 5.64287C9.64293 3.86768 8.20384 2.42859 6.42864 2.42859C4.65344 2.42859 3.21436 3.86768 3.21436 5.64287C3.21436 7.41807 4.65344 8.85716 6.42864 8.85716Z"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M0.642822 17.8571H6.42854H12.2142V17.1601C12.204 16.1802 11.9456 15.2187 11.463 14.3658C10.9805 13.5127 10.2897 12.7959 9.45502 12.2823C8.62036 11.7686 7.66913 11.4749 6.6902 11.4286C6.60293 11.4245 6.51568 11.4223 6.42854 11.4221C6.34139 11.4223 6.25414 11.4245 6.16687 11.4286C5.18794 11.4749 4.23671 11.7686 3.40205 12.2823C2.56741 12.7959 1.87655 13.5127 1.39403 14.3658C0.911507 15.2187 0.653058 16.1802 0.642822 17.1601V17.8571Z"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M11.5713 8.85716C13.3465 8.85716 14.7856 7.41807 14.7856 5.64287C14.7856 3.86768 13.3465 2.42859 11.5713 2.42859"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M14.7857 17.8573H17.3572V17.1601C17.3469 16.1802 17.0885 15.2187 16.6059 14.3658C16.1234 13.5127 15.4326 12.7959 14.5979 12.2823C14.0584 11.9503 13.4701 11.7101 12.8572 11.5693"
          stroke="#7D7D7D"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </g>
      <defs>
        <clipPath id="clip0_177_2929">
          <rect width="18" height="18" fill="white" transform="translate(0 0.5)" />
        </clipPath>
      </defs>
    </svg>
  );
};

export default TeamIcon;
