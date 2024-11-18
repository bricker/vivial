import { styled } from "@mui/material";
import Button, { ButtonProps } from "@mui/material/Button";
import React from "react";
import BackIcon from "../../Icons/BackIcon";

const CustumButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontFamily: theme.typography.fontFamily,
  fontWeight: 700,
  padding: "0 0 24px",
}));

const BackButton = (props: ButtonProps) => {
  return (
    <CustumButton onClick={props.onClick}>
      <BackIcon /> Back
    </CustumButton>
  );
};

export default BackButton;
