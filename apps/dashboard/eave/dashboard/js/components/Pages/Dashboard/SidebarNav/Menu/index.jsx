// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../../../types.js"; // eslint-disable-line no-unused-vars

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  menuList: {
    display: "flex",
    flexDirection: "column",
    listStyleType: "none",
    listStyle: "none",
    padding: 0,
    flexGrow: 1,
  },
}));

const Menu = (
  /** @type {{children: React.ReactNode}} */
  { children }
) => {
  const classes = makeClasses();
  return <nav className={classes.menuList}>{children}</nav>;
};

export default Menu;
