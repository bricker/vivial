import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import ChevronDownIcon from "../../Icons/ChevronDownIcon";
import ChevronUpIcon from "../../Icons/ChevronUpIcon";

interface DropdownButtonProps extends IconButtonProps {
  open: boolean;
  large?: boolean;
}

const DropdownButton = ({ open, large, ...props }: DropdownButtonProps) => {
  return (
    <IconButton {...props}>{open ? <ChevronUpIcon large={large} /> : <ChevronDownIcon large={large} />}</IconButton>
  );
};

export default DropdownButton;
