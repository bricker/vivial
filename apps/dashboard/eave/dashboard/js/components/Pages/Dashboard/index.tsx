import React, { useContext, useEffect, useState } from "react";

import { AppContext } from "$eave-dashboard/js/context/Provider";
import useAuth from "$eave-dashboard/js/hooks/useAuth";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { theme } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import { Outlet, useLocation } from "react-router-dom";
import { makeStyles } from "tss-react/mui";
import Glossary from "./Glossary";
import Insights from "./Insights";
import Settings from "./Settings";
import Setup from "./Setup";
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
  setupTab: { path: "/setup", component: <Setup /> },
  insightsTab: { path: "/insights", component: <Insights /> },
  glossaryTab: { path: "/glossary", component: <Glossary /> },
  settingsTab: { path: "/settings", component: <Settings /> },
  teamTab: { path: "/team", component: <TeamManagement /> },
};

const Dashboard = () => {
  const { classes } = makeClasses();

  const { userIsAuthed, validateUserAuth } = useAuth();
  const { getTeam, getClientCredentials } = useTeam();
  const { clientCredentialsNetworkStateCtx, dashboardNetworkStateCtx } = useContext(AppContext);
  const [credsNetworkState] = clientCredentialsNetworkStateCtx!;
  const [teamNetworkState] = dashboardNetworkStateCtx!;

  useEffect(() => {
    validateUserAuth();
    // load client creds so we can seamlessly determine which nav tabs to show
    // (i.e. should the setup tab be shown)
    getClientCredentials();
    // load team for subpage usage
    getTeam();
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

  // TODO: what to do if request errors?
  if (!userIsAuthed || credsNetworkState.credentialsAreLoading || teamNetworkState.teamIsLoading) {
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
