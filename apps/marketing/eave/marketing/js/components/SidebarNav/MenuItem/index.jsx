// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({}));

const MenuItem = ({
  /** @type {React.ReactNode} */ icon,
  /** @type {string} */ label,
  /** @type {boolean} */ expanded = false,
}) => {
  // TODO: when expanded, show alt text next to img icon
  return (
    <li>
      {icon}
      {expanded && <p>{label}</p>}
    </li>
  );
};

export default MenuItem;
