// @ts-check
import React, { useEffect, useState } from "react";

import { makeStyles } from "@material-ui/styles";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars
import GlossaryIcon from "../../Icons/GlossaryIcon.jsx";
import SettingsCogIcon from "../../Icons/SettingsCogIcon.jsx";
import SignOutIcon from "../../Icons/SignOutIcon.jsx";
import TeamIcon from "../../Icons/TeamIcon.jsx";
import EventGlossary from "./EventGlossary/index.jsx";
import Menu from "./SidebarNav/Menu/index.jsx";
import MenuItem from "./SidebarNav/MenuItem/index.jsx";
import SidebarNav from "./SidebarNav/index.jsx";

// TODO: a11y; the tabs arent kb navable

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  desktopContainer: {
    display: "flex",
    flexDirection: "row",
    height: "100vh",
  },
  mobileContainer: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    width: '100%',
  },
  spacer: {
    flexGrow: 1,
  },
}));

// sad enum replacement
const glossary = "glossary";
const configuration = "configuration";
const manage = "manage";
const logOut = "logOut";

function iconColor(isSelected) {
  return isSelected ? "white" : "black";
}

const EventDashboard = () => {
  const classes = makeClasses();

  const [selectedTab, setSelectedTab] = useState(glossary);
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    handleResize();

    // Add event listener for window resize
    window.addEventListener("resize", handleResize);
    // Remove event listener on component unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const container = isMobile ? classes.mobileContainer : classes.desktopContainer;

  return (
    <div className={container}>
      <SidebarNav hamburger={isMobile}>
        <Menu>
          <MenuItem
            label="Event Glossary"
            onClick={() => setSelectedTab(glossary)}
            selected={selectedTab === glossary}
            expanded={isMobile}
          >
            <GlossaryIcon color={iconColor(selectedTab === glossary)} />
          </MenuItem>

          {!isMobile && <div className={classes.spacer}></div>}

          <MenuItem
            label="Configuration"
            onClick={() => setSelectedTab(configuration)}
            selected={selectedTab === configuration}
            expanded={isMobile}
          >
            <SettingsCogIcon color={iconColor(selectedTab === configuration)} />
          </MenuItem>

          <MenuItem
            label="Team Management"
            onClick={() => setSelectedTab(manage)}
            selected={selectedTab === manage}
            expanded={isMobile}
          >
            <TeamIcon color={iconColor(selectedTab === manage)} />
          </MenuItem>

          <MenuItem
            label="Log Out"
            onClick={() => setSelectedTab(logOut)}
            selected={selectedTab === logOut}
            expanded={isMobile}
          >
            <SignOutIcon color={iconColor(selectedTab === logOut)} />
          </MenuItem>
        </Menu>
      </SidebarNav>
      {(() => {
        switch (selectedTab) {
          case configuration: // TODO: handle these pages/actions
          case manage:
          case logOut:
          default: // glossary
            return <EventGlossary />;
        }
      })()}
    </div>
  );
};

export default EventDashboard;
