import { styled } from "@mui/material";
import React from "react";
import { Link as BaseLink, LinkProps } from "react-router-dom";

const CustomLink = styled(BaseLink)(({ theme }) => ({
  color: theme.palette.primary.main,
  fontSize: "inherit",
  lineHeight: "inherit",
  "&:hover": {
    textDecoration: "underline",
  },
}));

interface CustomLinkProps extends LinkProps {
  underline?: boolean;
}

const Link = (props: CustomLinkProps) => {
  const textDecoration = props.underline ? "underline" : "none";
  return (
    <CustomLink to={props.to} sx={{ textDecoration }}>
      {props.children}
    </CustomLink>
  );
};

export default Link;
