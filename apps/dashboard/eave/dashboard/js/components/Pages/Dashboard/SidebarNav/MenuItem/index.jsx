// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React, { useCallback } from "react";
import * as Types from "../../../../../types.js"; // eslint-disable-line no-unused-vars
import { Link, Navigate } from "react-router-dom";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
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
  /** @type {{children: React.ReactNode, label: string, selected: boolean, expanded: boolean, to: string, reloadDocument?: boolean}} **/ {
  children,
  label,
  selected = false,
  expanded = false,
  to,
  reloadDocument = false,
}) => {
  const classes = makeClasses();

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
