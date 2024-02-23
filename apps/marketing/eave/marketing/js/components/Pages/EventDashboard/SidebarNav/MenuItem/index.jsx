// @ts-check
import { makeStyles } from "@material-ui/styles";
import classNames from "classnames";
import React from "react";
import * as Types from "../../../../../types.js"; // eslint-disable-line no-unused-vars

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  selectedBackground: {
    backgroundColor: "#0d81d9",
  },
  unselectedBackground: {
    backgroundColor: "transparent",
  },
  listItem: {
    display: "flex",
    flexDirection: "row",
    alignItems: 'center',
    gap: 12,
    fontSize: 24,
    padding: "24px 30px",
    "&:hover": {
      backgroundColor: "#0d81d988",
      cursor: "pointer",
    },
  },
  smallIcon: {
    width: 28,
    height: 28,
  },
  bigIcon: {
    width: 48,
    height: 48,
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

  const iconSize = expanded ? classes.bigIcon : classes.smallIcon;

  const background = selected
    ? classes.selectedBackground
    : classes.unselectedBackground;
  return (
    <li className={classNames(classes.listItem, background)} onClick={onClick}>
      <div className={iconSize}>{children}</div>
      {expanded && <p>{label}</p>}
    </li>
  );
};

export default MenuItem;
