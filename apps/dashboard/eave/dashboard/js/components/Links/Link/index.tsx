import { styled } from "@mui/material";
import React from "react";
import { Link as BaseLink, LinkProps } from "react-router-dom";

const CustomLink = styled(BaseLink)(({ theme }) => ({
  color: theme.palette.primary.main,
  fontSize: "inherit",
  lineHeight: "inherit",
  textDecoration: "none",
  "&:hover": {
    textDecoration: "underline",
  },
}));

const Link = (props: LinkProps) => {
  return <CustomLink {...props} />;
};

export default Link;
