import React from "react";
import { styled } from "@mui/material";
import Button, { ButtonProps } from "@mui/material/Button";

interface PillButtonProps extends ButtonProps {
  accentColor: string;
  selected: boolean;
  outlined?: boolean;
}

const CustomButton = styled(Button, {
  shouldForwardProp: (prop: string) => !["accentColor", "selected", "outlined"].includes(prop),
})<PillButtonProps>(({ accentColor, selected, outlined, theme }) => ({
  ...(outlined && {
  }),
  ...(selected && {
    backgroundColor: accentColor,
    border: "none",
  })
}));

const PillButton = (props: PillButtonProps) => {
  return <CustomButton {...props} />;
};

export default PillButton;
