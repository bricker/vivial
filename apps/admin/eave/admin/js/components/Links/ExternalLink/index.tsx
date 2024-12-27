import { styled } from "@mui/material";
import React from "react";

const CustomLink = styled("a")(({ theme }) => ({
  color: theme.palette.primary.main,
  fontSize: "inherit",
  lineHeight: "inherit",
  textDecoration: "none",
  "&:hover": {
    textDecoration: "underline",
  },
}));

interface ExternalLinkProps {
  to: string;
  children: React.ReactNode;
  target?: string;
}

const ExternalLink = ({ to, target = "_blank", ...props }: ExternalLinkProps) => {
  return <CustomLink href={to} target={target} {...props} />;
};

export default ExternalLink;
