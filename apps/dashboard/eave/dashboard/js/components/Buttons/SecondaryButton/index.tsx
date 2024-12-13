import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import BaseButton, { ButtonProps } from "@mui/material/Button";
import React from "react";

const CustomButton = styled(BaseButton)(({ theme }) => ({
  color: theme.palette.text.primary,
  backgroundColor: colors.secondaryButtonCTA,
  height: rem(52),
  borderRadius: 100,
  "&.Mui-disabled": {
    color: theme.palette.common.black,
    backgroundColor: theme.palette.text.disabled,
  },
  "&:hover, &:focus": {
    backgroundColor: colors.secondaryButtonCTA,
  },
}));

const SecondaryButton = (props: ButtonProps) => {
  return <CustomButton {...props} />;
};

export default SecondaryButton;
