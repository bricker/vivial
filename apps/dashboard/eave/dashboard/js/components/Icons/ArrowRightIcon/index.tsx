import React from "react";

const ArrowRightIcon = ({ width = 68, color = "black" }: { width?: number; color?: string }) => {
  const dimensionFactor = 0.38235294117647056;
  const height = width * dimensionFactor;
  return (
    <svg width={width} height={height} viewBox="0 0 68 26" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M47.152 25.84C47.792 24.176 48.496 22.64 49.264 21.232C50.032 19.76 50.896 18.384 51.856 17.104H0.400001V9.232H51.856C50.96 7.952 50.128 6.608 49.36 5.2C48.592 3.728 47.888 2.16 47.248 0.495996H54.544C58.512 5.168 62.864 8.72 67.6 11.152V15.28C62.864 17.584 58.512 21.104 54.544 25.84H47.152Z"
        fill={color}
      />
    </svg>
  );
};

export default ArrowRightIcon;
