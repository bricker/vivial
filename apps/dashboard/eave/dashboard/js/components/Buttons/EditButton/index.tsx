import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import React from "react";
import EditIcon from "../../Icons/EditIcon";

interface EditButtonProps extends IconButtonProps {
  small?: boolean;
}

const EditButton = ({ small = false, ...props }: EditButtonProps) => {
  return (
    <IconButton {...props}>
      <EditIcon small={small} />
    </IconButton>
  );
};

export default EditButton;
