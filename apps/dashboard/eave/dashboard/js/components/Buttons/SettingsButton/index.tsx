import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import SettingsIcon from "../../Icons/SettingsIcon";

interface SettingsButtonProps extends IconButtonProps {
  iconColor?: string;
}

const SettingsButton = ({ iconColor, ...props }: SettingsButtonProps) => {
  return (
    <IconButton {...props}>
      <SettingsIcon color={iconColor} />
    </IconButton>
  );
};

export default SettingsButton;
