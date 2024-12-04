import React from "react";
import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import EditIcon from "../../Icons/EditIcon";

const EditButton = (props: IconButtonProps) => {
  return (
    <IconButton {...props}>
      <EditIcon small/>
    </IconButton>
  );
};

export default EditButton;
