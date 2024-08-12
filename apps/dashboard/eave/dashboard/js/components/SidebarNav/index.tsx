import CloseIcon from "$eave-dashboard/js/components/Icons/CloseIcon";
import HamburgerIcon from "$eave-dashboard/js/components/Icons/HamburgerIcon";
import { imageUrl } from "$eave-dashboard/js/util/asset-util";
import classNames from "classnames";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  navbar: {
    backgroundColor: "#e5e9f5",
    width: "13rem",
    minWidth: "13rem",
    maxWidth: "13rem",
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
    alignItems: "center",
  },
  hamburgerButton: {
    border: "none",
    background: "transparent",
    margin: 24,
    cursor: "pointer",
  },
  coverMenu: {
    width: "100vw",
    height: "100vh",
    backgroundColor: "#fff",
    display: "flex",
    flexDirection: "column",
    overflow: "auto",
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
    cursor: "pointer",
    margin: 24,
  },
}));

const SidebarNav = ({ children, hamburger = false }: { children: React.ReactNode; hamburger?: boolean }) => {
  const location = useLocation();
  const { classes } = makeClasses();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    setMenuOpen(false);
  }, [location]);

  if (hamburger) {
    return (
      <div className={classes.hamburgerNav}>
        {!menuOpen && (
          <button className={classes.hamburgerButton} onClick={() => setMenuOpen(true)}>
            <HamburgerIcon stroke="#363636" />
          </button>
        )}
        {menuOpen && (
          <div className={classes.coverMenu}>
            <div className={classes.coverMenuHeader}>
              <img className={classes.logo} src={imageUrl("eave-e-logo-round-3x.png")} />
              <button className={classes.closeButton} onClick={() => setMenuOpen(false)}>
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
        <img className={classNames(classes.logo, classes.logoSeparation)} src={imageUrl("eave-e-logo-round-3x.png")} />
        {children}
      </div>
    );
  }
};

export default SidebarNav;
