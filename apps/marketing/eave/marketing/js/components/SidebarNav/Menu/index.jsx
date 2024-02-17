// @ts-check
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import { makeStyles } from "@material-ui/styles";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({}));

const Menu = ({/** @type {React.ReactNode} */ children}) => {
  return <ul>{children}</ul>;
};

export default Menu;