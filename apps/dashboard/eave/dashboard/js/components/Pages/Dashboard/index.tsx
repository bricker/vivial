import React, { useContext, useEffect, useState } from "react";

import { AppContext } from "$eave-dashboard/js/context/Provider";
import useAuth from "$eave-dashboard/js/hooks/useAuth";
import useTeam from "$eave-dashboard/js/hooks/useTeam";
import { theme } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import { makeStyles } from "tss-react/mui";
import PageRenderer from "../../Sidebar/PageRenderer";
import Sidebar from "../../Sidebar/index";
import Glossary from "./Glossary";
import Insights from "./Insights";
import Settings from "./Settings";
import Setup from "./Setup";
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
  screen: {
    display: "flex",
    flexDirection: "row",
  },
  sidebar: {
    height: "100vh",
    position: "sticky",
    top: 0,
  },
  content: {
    flexGrow: 1,
    overflowX: "hidden",
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
      <div className={classes.screen}>
        <div className={classes.sidebar}>
          <Sidebar />
        </div>
        <div className={classes.content}>
          <PageRenderer />
        </div>
      </div>
    );
  }
};

export { Dashboard };
