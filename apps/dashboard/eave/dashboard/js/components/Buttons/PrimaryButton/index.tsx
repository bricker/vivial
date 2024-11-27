import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import BaseButton, { ButtonProps } from "@mui/material/Button";
import React from "react";

const CustomButton = styled(BaseButton)(({ theme }) => ({
  color: theme.palette.common.black,
  backgroundColor: theme.palette.primary.main,
  height: rem("52px"),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
  "&:hover, &:focus": {
    backgroundColor: theme.palette.primary.main,
  },
}));

const PrimaryButton = (props: ButtonProps) => {
  return <CustomButton {...props} />;
};

export default PrimaryButton;
