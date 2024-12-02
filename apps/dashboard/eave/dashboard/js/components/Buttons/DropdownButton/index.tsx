import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import ChevronDownIcon from "../../Icons/ChevronDownIcon";
import ChevronUpIcon from "../../Icons/ChevronUpIcon";

interface DropdownButtonProps extends IconButtonProps {
  open: boolean;
}

const DropdownButton = ({ open, ...props }: DropdownButtonProps) => {
  return <IconButton {...props}>{open ? <ChevronUpIcon /> : <ChevronDownIcon />}</IconButton>;
};

export default DropdownButton;
