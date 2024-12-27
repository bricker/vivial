import { fontFamilies } from "$eave-admin/js/theme/fonts";
import { rem } from "$eave-admin/js/theme/helpers/rem";
import { styled } from "@mui/material";
import Button, { ButtonProps } from "@mui/material/Button";
import React from "react";

interface PillButtonProps extends ButtonProps {
  accentColor: string;
  selected: boolean;
  outlined?: boolean;
}

const CustomButton = styled(Button, {
  shouldForwardProp: (prop: string) => !["accentColor", "selected", "outlined"].includes(prop),
})<PillButtonProps>(({ accentColor, selected, outlined, theme }) => ({
  color: theme.palette.grey[300],
  backgroundColor: theme.palette.grey[900],
  fontFamily: fontFamilies.inter,
  fontSize: rem(14),
  lineHeight: rem(17),
  borderRadius: 24,
  fontWeight: 500,
  minWidth: 0,
  height: 32,
  padding: "0px 20px",
  margin: "0px 5px 9px 0px",
  boxSizing: "border-box",
  border: `1px solid transparent`, // prevents resizing of outlined buttons
  ...(outlined && {
    border: `1px solid ${theme.palette.grey[300]}`,
  }),
  ...(selected && {
    color: theme.palette.field.secondary,
    backgroundColor: accentColor,
    border: `1px solid transparent`,
  }),
}));

const PillButton = (props: PillButtonProps) => {
  return <CustomButton {...props} />;
};

export default PillButton;
