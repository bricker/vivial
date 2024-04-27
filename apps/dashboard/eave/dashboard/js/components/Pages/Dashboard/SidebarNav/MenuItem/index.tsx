import classNames from "classnames";
import React from "react";
import { Link } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  selectedBackground: {
    backgroundColor: "#0d81d9",
    color: "white",
  },
  unselectedBackground: {
    backgroundColor: "transparent",
  },
  listItem: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    fontSize: 24,
    padding: "24px 30px",
    border: "none",
    "&:hover": {
      backgroundColor: "#0d81d988",
      cursor: "pointer",
    },
  },
}));

const MenuItem = (
  {
    children,
    label,
    to,
    selected = false,
    expanded = false,
    reloadDocument = false,
  }:
  {
    children: React.ReactNode;
    label: string;
    to: string,
    selected?: boolean;
    expanded?: boolean;
    reloadDocument?: boolean;
  }
) => {
  const {classes} = makeClasses();

  const background = selected
    ? classes.selectedBackground
    : classes.unselectedBackground;

  return (
    <Link
      className={classNames(classes.listItem, background)}
      aria-label={label}
      to={to}
      reloadDocument={reloadDocument}
    >
      {children}
      {expanded && <p>{label}</p>}
    </Link>
  );
};

export default MenuItem;
