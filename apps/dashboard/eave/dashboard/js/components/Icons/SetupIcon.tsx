import React from "react";

const SetupIcon = ({ color = "black" }: { color?: string }) => {
  return (
    <svg
      style={{ width: 40, height: 40 }}
      width="18"
      height="18"
      viewBox="0 0 18 18"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g>
        <path
          d="M0.642857 14.1002H17.3571"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M14.1429 17.3144L17.3571 14.1001L14.1429 10.8859"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M2.82866 7.42818V1.94208C2.82866 2.69954 2.2146 3.31359 1.45714 3.31359H0.99996"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M4.65725 7.42834H0.999851"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M10.8287 7.42818H7.17125V6.64887C7.17125 6.10396 7.49382 5.61075 7.99304 5.39233L10.0282 4.50196C10.5144 4.28921 10.8287 3.80879 10.8287 3.27802C10.8287 2.5402 10.2305 1.94208 9.49271 1.94208H8.54277C7.9456 1.94208 7.43757 2.32373 7.24929 2.85643"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M15.6642 4.45667C16.4217 4.45667 17.0357 5.07072 17.0357 5.82819V6.05679C17.0357 6.81425 16.4217 7.42831 15.6642 7.42831L14.7498 7.42832C14.1526 7.42832 13.6446 7.04666 13.4564 6.51395"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M13.6543 2.85643C13.8036 2.32874 14.2887 1.94209 14.8641 1.94208H15.5499C16.2444 1.94206 16.8072 2.50495 16.8072 3.19931C16.8072 3.89366 16.2444 4.45655 15.5499 4.45655L15.4356 4.45654"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </svg>
  );
};

export default SetupIcon;
