// @ts-check
import React from "react";

const GraphIcon = ({ /** @type {string} */ color = "black" }) => {
  return (
    <svg
      width="41"
      height="40"
      viewBox="0 0 41 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M30.5278 14L23.2535 24.6166C22.8254 25.2413 21.8853 25.182 21.5391 24.5085L18.961 19.4915C18.6148 18.818 17.6747 18.7587 17.2466 19.3834L9.97228 30"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect
        x="1.75"
        y="2"
        width="37"
        height="36"
        rx="2"
        stroke={color}
        strokeWidth="3"
      />
    </svg>
  );
};

export default GraphIcon;
