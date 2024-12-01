import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { styled } from "@mui/material";
import BaseButton, { ButtonProps } from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import React from "react";

interface HighlightButtonProps extends ButtonProps {
  highlighted: boolean;
  highlightColor: string;
}

const Button = styled(BaseButton, {
  shouldForwardProp: (prop: string) => !["highlighted", "highlightColor"].includes(prop),
})<HighlightButtonProps>(({ highlighted, highlightColor, theme }) => ({
  fontFamily: fontFamilies.inter,
  backgroundColor: theme.palette.grey[900],
  color: theme.palette.grey[300],
  display: "flex",
  alignItems: "center",
  minWidth: 0,
  padding: "0 16px",
  height: 40,
  borderRadius: "111.889px",
  maxWidth: 255,
  fontWeight: 400,
  ...(highlighted && {
    border: `1.039px solid ${highlightColor}`,
    color: highlightColor,
    fontWeight: 500,
  }),
}));

const ButtonText = styled(Typography)(() => ({
  fontFamily: "inherit",
  fontWeight: "inherit",
  fontSize: "inherit",
  color: "inherit",
}));

const HighlightButton = ({ children, ...props }: HighlightButtonProps) => {
  return (
    <Button {...props}>
      <ButtonText noWrap>{children}</ButtonText>
    </Button>
  );
};

export default HighlightButton;
