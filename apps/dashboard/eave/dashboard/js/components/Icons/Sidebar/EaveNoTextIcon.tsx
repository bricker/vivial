import { motion } from "framer-motion";
import React from "react";

interface LogoIconProps {
  color?: string;
  width?: string;
  height?: string;
  isHovering: boolean;
}

const EaveNoTextIcon: React.FC<LogoIconProps> = ({ color = "black", width = "32px", height = "32px", isHovering }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }} // Duration for the transition
    >
      {!isHovering ? (
        <motion.svg
          key="icon1" // Unique key for this component
          width={width}
          height={height}
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }} // Duration for the transition
        >
          <circle cx="16.2534" cy="15.8096" r="15.4899" fill={color} />
          <rect x="10.4446" y="6.70901" width="2.90436" height="18.2007" rx="1.45218" fill="white" />
          <rect x="10.4446" y="6.51559" width="11.6175" height="2.90436" rx="1.45218" fill="white" />
          <rect x="10.4446" y="22.2185" width="11.6175" height="2.90436" rx="1.45218" fill="white" />
          <circle cx="17.5313" cy="15.9064" r="1.45218" fill="white" />
        </motion.svg>
      ) : (
        <motion.svg
          key="arrow" // Unique key for this component
          width={width}
          height={height}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }} // Duration for the transition
        >
          <rect width="24" height="24" fill="none" />
          <path d="M9.5 7L14.5 12L9.5 17" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" />
        </motion.svg>
      )}
    </motion.div>
  );
};

export default EaveNoTextIcon;
