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
  preserveQueryParams?: boolean;
}

const Link = (props: CustomLinkProps) => {
  const textDecoration = props.underline ? "underline" : "none";
  let to = props.to;

  if (props.preserveQueryParams ?? false) {
    if (typeof props.to === "string") {
      // FIXME: This assumes `props.to` doesn't contain any query params.
      to = `${props.to}${window.location.search}`;
    } else {
      // FIXME: This assumes `props.to` doesn't contain any query params.
      to = { ...props.to, search: window.location.search };
    }
  }

  return (
    <CustomLink to={to} sx={{ textDecoration }}>
      {props.children}
    </CustomLink>
  );
};

export default Link;
