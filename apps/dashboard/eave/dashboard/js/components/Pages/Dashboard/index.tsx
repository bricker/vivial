import React, { useEffect, useState } from "react";

import GlossaryIcon from "$eave-dashboard/js/components/Icons/GlossaryIcon";
import GraphIcon from "$eave-dashboard/js/components/Icons/GraphIcon";
import SettingsCogIcon from "$eave-dashboard/js/components/Icons/SettingsCogIcon";
import SignOutIcon from "$eave-dashboard/js/components/Icons/SignOutIcon";
import TeamIcon from "$eave-dashboard/js/components/Icons/TeamIcon";
import useAuth from "$eave-dashboard/js/hooks/useAuth";
import { theme } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import { makeStyles } from "tss-react/mui";
import NotFound from "../NotFound";
import Glossary from "./Glossary";
import Insights from "./Insights";
import Settings from "./Settings";
import SidebarNav from "./SidebarNav";
import Menu from "./SidebarNav/Menu";
import MenuItem from "./SidebarNav/MenuItem";
import TeamManagement from "./TeamManagement";

const makeClasses = makeStyles()(() => ({
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
  spacer: {
    flexGrow: 1,
  },
  loader: {
    display: "flex",
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 32,
  },
}));

function iconColor(isSelected: boolean): "white" | "black" {
  return isSelected ? "white" : "black";
}

const Dashboard = ({
  page = "insights",
}: {
  page?: "insights" | "glossary" | "settings" | "team";
}) => {
  const { classes } = makeClasses();

  // const { userIsAuthed, validateUserAuth } = useAuth();

  // useEffect(() => {
  //   validateUserAuth();
  // }, [page]);

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

  const container = usingMobileLayout
    ? classes.mobileContainer
    : classes.desktopContainer;

  const nav = (
    <SidebarNav hamburger={usingMobileLayout}>
      <Menu>
        <MenuItem
          label="Insights"
          to="/insights"
          selected={page === "insights"}
          expanded={usingMobileLayout}
        >
          <GraphIcon color={iconColor(page === "insights")} />
        </MenuItem>

        <MenuItem
          label="Event Glossary"
          to="/glossary"
          selected={page === "glossary"}
          expanded={usingMobileLayout}
        >
          <GlossaryIcon color={iconColor(page === "glossary")} />
        </MenuItem>

        {!usingMobileLayout && <div className={classes.spacer}></div>}

        <MenuItem
          label="Settings"
          to="/settings"
          selected={page === "settings"}
          expanded={usingMobileLayout}
        >
          <SettingsCogIcon color={iconColor(page === "settings")} />
        </MenuItem>

        <MenuItem
          label="Team Management"
          to="/team"
          selected={page === "team"}
          expanded={usingMobileLayout}
        >
          <TeamIcon color={iconColor(page === "team")} />
        </MenuItem>

        <MenuItem
          label="Log Out"
          to="/logout"
          reloadDocument={true}
          selected={false}
          expanded={usingMobileLayout}
        >
          <SignOutIcon color={iconColor(false)} />
        </MenuItem>
      </Menu>
    </SidebarNav>
  );

  let pageComponent: React.ReactElement;

  switch (page) {
    case "insights":
      pageComponent = <Insights />;
      break;
    case "glossary":
      pageComponent = <Glossary />;
      break;
    case "settings":
      pageComponent = <Settings />;
      break;
    case "team":
      pageComponent = <TeamManagement />;
      break;
    default:
      pageComponent = <NotFound />;
      break;
  }

  // if (!userIsAuthed) {
  //   return (
  //     <div className={container}>
  //       <div className={classes.loader}>
  //         <CircularProgress color="secondary" />
  //       </div>
  //     </div>
  //   );
  // } else {
    return (
      <div className={container}>
        {nav}
        {pageComponent}
      </div>
    );
  // }
};

export default Dashboard;
