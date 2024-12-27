import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import CloseIcon from "../../Icons/CloseIcon";

interface CloseButonProps extends IconButtonProps {
  iconColor?: string;
}

const CloseButton = ({ iconColor, ...props }: CloseButonProps) => {
  return (
    <IconButton {...props}>
      <CloseIcon color={iconColor} />
    </IconButton>
  );
};

export default CloseButton;
