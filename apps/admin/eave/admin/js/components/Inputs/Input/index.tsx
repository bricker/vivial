import { styled } from "@mui/material";
import BaseInput, { InputProps } from "@mui/material/Input";
import React from "react";

import { rem } from "../../../theme/helpers/rem";

const CustomInput = styled(BaseInput)(({ theme }) => ({
  backgroundColor: theme.palette.field.primary,
  height: rem(55),
  borderRadius: 100,
  padding: "0 16px",
  "input::placeholder": {
    color: theme.palette.text.secondary,
  },
}));

const Input = (props: InputProps) => {
  return <CustomInput fullWidth disableUnderline {...props} />;
};

export default Input;
