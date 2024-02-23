// @ts-check
import { makeStyles } from "@material-ui/styles";
import React, { useState } from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import { imageUrl } from "../../../../util/asset-util.js";
import CloseIcon from "../../../Icons/CloseIcon.js";
import HamburgerIcon from "../../../Icons/HamburgerIcon.js";
import classNames from "classnames";

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
  },
  logoSeparation: {
    marginBottom: 96,
  },
  hamburgerNav: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "flex-end",
    alignItems: 'center',
  },
  hamburgerButton: {
    border: "none",
    background: "transparent",
    margin: 24,
    cursor: 'pointer',
  },
  coverMenu: {
    width: "100vw",
    height: "100vh",
    backgroundColor: "#fff",
    display: "flex",
    flexDirection: "column",
  },
  coverMenuHeader: {
    display: "flex",
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
  },
  closeButton: {
    border: "none",
    backgroundColor: "transparent",
    cursor: 'pointer',
    margin: 24,
  },
}));

const SidebarNav = ({
  /** @type {React.ReactNode} */ children,
  /** @type {boolean} */ hamburger = false,
}) => {
  const classes = makeClasses();
  const [menuOpen, setMenuOpen] = useState(false);

  if (hamburger) {
    return (
      <div className={classes.hamburgerNav}>
        {!menuOpen && (
          <button
            className={classes.hamburgerButton}
            onClick={() => setMenuOpen(true)}
          >
            <HamburgerIcon stroke="#363636" />
          </button>
        )}
        {menuOpen && (
          <div className={classes.coverMenu}>
            <div className={classes.coverMenuHeader}>
              <img
                className={classes.logo}
                src={imageUrl("eave-e-logo-round-3x.png")}
              />
              <button
                className={classes.closeButton}
                onClick={() => setMenuOpen(false)}
              >
                <CloseIcon stroke="#363636" />
              </button>
            </div>
            {children}
          </div>
        )}
      </div>
    );
  } else {
    return (
      <div className={classes.navbar}>
        <img
          className={classNames(classes.logo, classes.logoSeparation)}
          src={imageUrl("eave-e-logo-round-3x.png")}
        />
        {children}
      </div>
    );
  }
};

export default SidebarNav;
