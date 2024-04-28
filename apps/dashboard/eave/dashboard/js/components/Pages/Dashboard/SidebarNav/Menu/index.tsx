import React from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  menuList: {
    display: "flex",
    flexDirection: "column",
    listStyleType: "none",
    listStyle: "none",
    padding: 0,
    flexGrow: 1,
  },
}));

const Menu = ({ children }: { children: React.ReactNode }) => {
  const { classes } = makeClasses();
  return <nav className={classes.menuList}>{children}</nav>;
};

export default Menu;
