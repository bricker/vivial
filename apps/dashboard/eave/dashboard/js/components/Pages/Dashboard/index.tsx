import React, { useEffect, useState } from "react";

import useAuth from "$eave-dashboard/js/hooks/useAuth";
import { theme } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import { Outlet, useLocation } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import Glossary from "./Glossary";
import Insights from "./Insights";
import Settings from "./Settings";
import TabbedNav from "./TabbedNav";
import TeamManagement from "./TeamManagement";

const makeClasses = makeStyles()(() => ({
  sharedContainer: {
    backgroundColor: "white",
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  desktopContainer: {
    display: "flex",
    flexDirection: "row",
    height: "100vh",
  },
  mobileContainer: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    width: "100%",
  },
  loader: {
    display: "flex",
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 32,
  },
}));

// tab pages that should be rendered
const tabs = {
  insightsTab: { path: "/insights", component: <Insights /> },
  glossaryTab: { path: "/glossary", component: <Glossary /> },
  settingsTab: { path: "/settings", component: <Settings /> },
  teamTab: { path: "/team", component: <TeamManagement /> },
};

const Dashboard = () => {
  const { classes } = makeClasses();

  const { userIsAuthed, validateUserAuth } = useAuth();

  useEffect(() => {
    validateUserAuth();
  }, []);

  const [usingMobileLayout, setUsingMobileLayout] = useState(false);
  useEffect(() => {
    const handleResize = () => {
      setUsingMobileLayout(window.innerWidth <= theme.breakpoints.values.md);
    };

    handleResize();

    // Add event listener for window resize
    window.addEventListener("resize", handleResize);
    // Remove event listener on component unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const container = classNames({
    [classes.sharedContainer]: true,
    [classes.mobileContainer]: usingMobileLayout,
    [classes.desktopContainer]: !usingMobileLayout,
  });

  const initialLocation = window.location.pathname;

  if (!userIsAuthed) {
    return (
      <div className={container}>
        <div className={classes.loader}>
          <CircularProgress color="secondary" />
        </div>
      </div>
    );
  } else {
    return (
      <>
        {Object.entries(tabs).map(([key, tab]) => (
          <div
            id={key}
            key={key}
            className={container}
            style={{ visibility: tab.path === initialLocation ? "visible" : "hidden" }}
          >
            <TabbedNav />
            {tab.component}
          </div>
        ))}
        <Outlet />
      </>
    );
  }
};

type TabKey = keyof typeof tabs;
const TabRevealer = ({ name, pathname }: { name: TabKey; pathname: string }) => {
  const location = useLocation();
  if (location.pathname === pathname) {
    for (const tabKey of Object.keys(tabs)) {
      const tabUI = document.getElementById(tabKey);
      if (tabUI) {
        // hide all tabs that don't match name
        tabUI.style.visibility = tabKey === name ? "visible" : "hidden";
      }
    }
  }
  // return empty html so as to not cover the visible insights tab
  return <></>;
};

export { Dashboard, TabRevealer };
