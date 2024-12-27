import { styled } from "@mui/material";
import React from "react";

import Typography from "@mui/material/Typography";
import ErrorIcon from "../../Icons/ErrorIcon";

const ErrorContainer = styled("div")(() => ({
  display: "flex",
}));

const ErrorMessage = styled(Typography)(({ theme }) => ({
  color: theme.palette.error.main,
  marginLeft: 4,
  fontSize: "inherit",
  lineHeight: "inherit",
}));

interface InputErrorProps {
  children: React.ReactNode;
}

const InputError = ({ children }: InputErrorProps) => {
  return (
    <ErrorContainer>
      <ErrorIcon />
      <ErrorMessage>{children}</ErrorMessage>
    </ErrorContainer>
  );
};

export default InputError;
