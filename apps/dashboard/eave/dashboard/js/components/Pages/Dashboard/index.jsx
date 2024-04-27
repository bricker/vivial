// @ts-check
import React, { useEffect, useState } from "react";

import { makeStyles } from "@material-ui/styles";
import { theme } from "../../../theme.js";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import GlossaryIcon from "../../Icons/GlossaryIcon.jsx";
import GraphIcon from "../../Icons/GraphIcon.jsx";
import SettingsCogIcon from "../../Icons/SettingsCogIcon.jsx";
import SignOutIcon from "../../Icons/SignOutIcon.jsx";
import TeamIcon from "../../Icons/TeamIcon.jsx";
import Insights from "./Insights/index.jsx";
import Glossary from "./Glossary/index.jsx";
import Menu from "./SidebarNav/Menu/index.jsx";
import MenuItem from "./SidebarNav/MenuItem/index.jsx";
import SidebarNav from "./SidebarNav/index.jsx";
import NotFound from "../NotFound/index.jsx";
import Settings from "./Settings/index.jsx";
import TeamManagement from "./TeamManagement/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ _theme) => ({
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
}));

function iconColor(/** @type {boolean} */ isSelected) {
  return isSelected ? "white" : "black";
}

const Dashboard = (/** @type {{ page: "insights" | "glossary" | "settings" | "team" }} */ { page = "insights" }) => {
  const classes = makeClasses();

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

  /** @type {JSX.Element} */
  let pageComponent;

  switch (page) {
    case "insights":
      pageComponent = <Insights />
      break;
    case "glossary":
      pageComponent = <Glossary />
      break;
    case "settings":
      pageComponent = <Settings />
      break;
    case "team":
      pageComponent = <TeamManagement />
      break;
    default:
      pageComponent = <NotFound />
      break;
  }

  return (
    <div className={container}>
      {nav}
      {pageComponent}
    </div>
  );
};

export default Dashboard;
