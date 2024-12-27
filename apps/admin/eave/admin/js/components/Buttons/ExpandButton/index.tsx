import { rem } from "$eave-admin/js/theme/helpers/rem";
import { styled } from "@mui/material";
import Button, { ButtonProps } from "@mui/material/Button";
import React from "react";

import Typography from "@mui/material/Typography";
import ChevronDownIcon from "../../Icons/ChevronDownIcon";
import ChevronUpIcon from "../../Icons/ChevronUpIcon";

const CustomButton = styled(Button)(() => ({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  backgroundColor: "#3B3B3B", // one-off color
  height: 30,
  width: 92,
  borderRadius: "24px",
}));

const CTA = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: rem(10),
  lineHeight: rem(12),
  marginBottom: 1,
  marginRight: 1,
}));

interface ExpandButtonProps extends ButtonProps {
  expanded: boolean;
}

const ExpandButton = ({ expanded, ...props }: ExpandButtonProps) => {
  const cta = expanded ? "See less" : "See more";
  const Icon = expanded ? ChevronUpIcon : ChevronDownIcon;
  return (
    <CustomButton {...props}>
      <CTA>{cta}</CTA> <Icon thin />
    </CustomButton>
  );
};

export default ExpandButton;
