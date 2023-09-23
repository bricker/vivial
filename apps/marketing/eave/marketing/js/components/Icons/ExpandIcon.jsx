import React from 'react';

const ExpandIcon = ({ color, up }) => {
  const stroke = color || "#0092C7";
  if (up) {
    return (
      <svg width="25" height="25" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path stroke={stroke} d="M6.25 15.625L12.5 9.375L18.75 15.625" />
    </svg>
    );
  }
  return (
  <svg width="25" height="25" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path stroke={stroke} d="M18.75 9.375L12.5 15.625L6.25 9.375" />
  </svg>
  );
};

export default ExpandIcon;
