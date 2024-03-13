// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React from "react";
import * as Types from "../../../../../types.js"; // eslint-disable-line no-unused-vars

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

const MenuItem = ({
  /** @type {React.ReactNode} */ children,
  /** @type {string} */ label,
  /** @type {function} */ onClick,
  /** @type {boolean} */ selected = false,
  /** @type {boolean} */ expanded = false,
}) => {
  const classes = makeClasses();

  const background = selected
    ? classes.selectedBackground
    : classes.unselectedBackground;
  return (
    <button
      className={classNames(classes.listItem, background)}
      aria-label={label}
      onClick={onClick}
    >
      {children}
      {expanded && <p>{label}</p>}
    </button>
  );
};

export default MenuItem;
