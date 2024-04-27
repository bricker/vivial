import { Button as MaterialButton } from "@mui/material";
import classNames from "classnames";
import React from "react";
import { Link } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  root: {
    minWidth: 172,
    minHeight: 50,
    textTransform: "none",
    borderRadius: "10px",
    fontSize: 16,
  },
  disabled: {
    backgroundColor: "#808182 !important",
    color: "#FFFFFF !important",
  },
  link: {
    textDecoration: "none",
  },
}));

const Button = (
  {
    children,
    className,
    to,
    target,
    color = "primary",
    variant = "contained",
    ...rest
  }:
  {
    children: React.ReactNode;
    className: string;
    to?: string;
    target?: string;
    color?: "inherit" | "primary" | "secondary" | "success" | "error" | "info" | "warning";
    variant: "text" | "outlined" | "contained";
    [key:string]: any;
  },
) => {
  const { classes } = makeClasses();
  const rootClass = classNames(classes.root, className);

  const button = (
    <MaterialButton
      classes={{
        root: rootClass,
        disabled: classes.disabled,
      }}
      color={color}
      variant={variant}
      {...rest}
    >
      {children}
    </MaterialButton>
  );

  if (to) {
    return (
      <Link className={classes.link} to={to} target={target}>
        {button}
      </Link>
    );
  }

  return button;
};

export default Button;
