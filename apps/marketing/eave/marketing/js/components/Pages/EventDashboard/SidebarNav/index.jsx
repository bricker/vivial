// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import { imageUrl } from "../../../../util/asset-util.js";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  navbar: {
    backgroundColor: "#e5e9f5",
    height: "100%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    paddingBottom: 60,
  },
  logo: {
    width: 60,
    height: 60,
    margin: 24,
    marginBottom: 96,
  },
}));

// TODO: if mobile, collaps to top-right burger menue
const SidebarNav = ({ /** @type {React.ReactNode} */ children }) => {
  const classes = makeClasses();

  return (
    <div className={classes.navbar}>
      <img
        className={classes.logo}
        src={imageUrl("eave-e-logo-round-3x.png")}
      />
      {children}
    </div>
  );
};

export default SidebarNav;
