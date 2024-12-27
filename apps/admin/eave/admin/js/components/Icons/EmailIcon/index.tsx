import React from "react";
import { colors } from "../../../theme/colors";
import { IconProps } from "../types";

const EmailIcon = ({ width = 13, height = 10, color = colors.whiteText }: IconProps) => {
  const viewBox = `0 0 ${width} ${height}`;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox={viewBox} fill="none">
      <path
        fill={color}
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11.8073 0C12.1969 0 12.5428 0.178175 12.7604 0.453767L6.43911 5.51234L0.174106 0.545626C0.383578 0.218409 0.761388 0 1.19266 0H11.8073ZM0 8.42087V1.44325L4.49531 5.007L0.0092667 8.56341C0.00315199 8.51672 0 8.46914 0 8.42087ZM0.411124 9.28048C0.620436 9.45387 0.893702 9.55882 1.19266 9.55882H11.8073C12.0643 9.55882 12.3023 9.48129 12.497 9.34941L7.72018 5.52683L6.86118 6.21423C6.61824 6.40865 6.26432 6.40943 6.02044 6.21608L5.14849 5.52483L0.411124 9.28048ZM8.36977 5.007L12.9674 8.68621C12.9887 8.60108 13 8.51223 13 8.42087V1.30171L8.36977 5.007Z"
      />
    </svg>
  );
};

export default EmailIcon;
