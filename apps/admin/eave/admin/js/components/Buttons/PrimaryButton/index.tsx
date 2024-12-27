import { rem } from "$eave-admin/js/theme/helpers/rem";
import { styled } from "@mui/material";
import BaseButton, { ButtonProps } from "@mui/material/Button";
import React from "react";

interface PrimaryButtonProps extends ButtonProps {
  bg?: string;
}

const CustomButton = styled(BaseButton, {
  shouldForwardProp: (prop) => prop !== "bg",
})<PrimaryButtonProps>(({ bg, theme }) => ({
  color: theme.palette.common.black,
  backgroundColor: bg || theme.palette.primary.main,
  height: rem(52),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
  "&:hover, &:focus": {
    backgroundColor: bg || theme.palette.primary.main,
  },
}));

const PrimaryButton = (props: PrimaryButtonProps) => {
  return <CustomButton {...props} />;
};

export default PrimaryButton;
