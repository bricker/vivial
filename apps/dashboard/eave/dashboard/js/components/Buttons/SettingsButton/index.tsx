import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import SearchIcon from "../../Icons/SearchIcon";

interface SettingsButtonProps extends IconButtonProps {
  iconColor?: string;
}

const SettingsButton = ({ iconColor, ...props }: SettingsButtonProps) => {
  return (
    <IconButton {...props}>
      <SearchIcon color={iconColor} />
    </IconButton>
  );
};

export default SettingsButton;
