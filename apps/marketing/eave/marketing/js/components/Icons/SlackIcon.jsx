import React from 'react';

function SlackIcon({ className }) {
  return (
    <svg
    className={className}
      xmlns="http://www.w3.org/2000/svg"
      fill="#fff"
      fillRule="evenodd"
      stroke="#000"
      strokeLinecap="round"
      strokeLinejoin="round"
      viewBox="0 0 64 64"
    >
      <path
        fill="#e01e5a"
        stroke="#e01e5a"
        strokeWidth="0.79"
        d="M17.778 40.31c0-3.728 2.819-6.73 6.32-6.73 3.503 0 6.322 3.002 6.322 6.73v16.565c0 3.728-2.82 6.73-6.321 6.73-3.502 0-6.321-3.002-6.321-6.73z"
      ></path>
      <path
        fill="#ecb22d"
        stroke="#ecb22d"
        strokeWidth="0.79"
        d="M40.31 46.222c-3.728 0-6.73-2.819-6.73-6.32 0-3.503 3.002-6.322 6.73-6.322h16.565c3.728 0 6.73 2.82 6.73 6.321 0 3.502-3.002 6.321-6.73 6.321z"
      ></path>
      <path
        fill="#2fb67c"
        stroke="#2fb67c"
        strokeWidth="0.79"
        d="M33.58 7.125c0-3.728 2.82-6.73 6.321-6.73 3.502 0 6.321 3.002 6.321 6.73V23.69c0 3.728-2.819 6.73-6.32 6.73-3.503 0-6.322-3.002-6.322-6.73z"
      ></path>
      <path
        fill="#36c5f1"
        stroke="#36c5f1"
        strokeWidth="0.79"
        d="M7.125 30.42c-3.728 0-6.73-2.82-6.73-6.321 0-3.502 3.002-6.321 6.73-6.321H23.69c3.728 0 6.73 2.819 6.73 6.32 0 3.503-3.002 6.322-6.73 6.322z"
      ></path>
      <g strokeLinejoin="miter" strokeWidth="0.79">
        <path
          fill="#ecb22d"
          stroke="#ecb22d"
          d="M33.58 57.284a6.308 6.308 0 006.321 6.32 6.307 6.307 0 006.321-6.32 6.308 6.308 0 00-6.32-6.321H33.58z"
        ></path>
        <path
          fill="#2fb67c"
          stroke="#2fb67c"
          d="M57.284 30.42h-6.321v-6.321a6.307 6.307 0 016.321-6.321 6.307 6.307 0 016.32 6.32 6.307 6.307 0 01-6.32 6.322z"
        ></path>
        <path
          fill="#e01e5a"
          stroke="#e01e5a"
          d="M6.716 33.58h6.321v6.321a6.307 6.307 0 01-6.32 6.321 6.308 6.308 0 01-6.322-6.32 6.307 6.307 0 016.321-6.322z"
        ></path>
        <path
          fill="#36c5f1"
          stroke="#36c5f1"
          d="M30.42 6.716v6.321h-6.321a6.308 6.308 0 01-6.321-6.321 6.307 6.307 0 016.32-6.32 6.308 6.308 0 016.322 6.32z"
        ></path>
      </g>
    </svg>
  );
}

export default SlackIcon;
