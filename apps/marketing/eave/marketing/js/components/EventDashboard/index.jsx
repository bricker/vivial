// @ts-check
import React, { useState } from "react";

import { makeStyles } from "@material-ui/styles";
import * as Types from "../../types.js"; // eslint-disable-line no-unused-vars
import GlossaryIcon from "../Icons/GlossaryIcon.jsx";
import SettingsCogIcon from "../Icons/SettingsCogIcon.jsx";
import SignOutIcon from "../Icons/SignOutIcon.jsx";
import TeamIcon from "../Icons/TeamIcon.jsx";
import Menu from "./SidebarNav/Menu/index.jsx";
import MenuItem from "./SidebarNav/MenuItem/index.jsx";
import SidebarNav from "./SidebarNav/index.jsx";
import EventGlossary from "./EventGlossary/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  container: {
    display: "flex",
    flexDirection: "row",
    height: "100vh",
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
  // TODO: rest of the page based on tab selected
  const expanded = true;

  const classes = makeClasses();

  const [selectedTab, setSelectedTab] = useState(glossary);

  return (
    <div className={classes.container}>
      <SidebarNav>
        <Menu>
          <MenuItem
            label="Event Glossary"
            onClick={() => setSelectedTab(glossary)}
            selected={selectedTab === glossary}
          >
            <GlossaryIcon color={iconColor(selectedTab === glossary)} />
          </MenuItem>

          {expanded && <div className={classes.spacer}></div>}

          <MenuItem
            label="Configuration"
            onClick={() => setSelectedTab(configuration)}
            selected={selectedTab === configuration}
          >
            <SettingsCogIcon color={iconColor(selectedTab === configuration)} />
          </MenuItem>

          <MenuItem
            label="Team Management"
            onClick={() => setSelectedTab(manage)}
            selected={selectedTab === manage}
          >
            <TeamIcon color={iconColor(selectedTab === manage)} />
          </MenuItem>

          <MenuItem
            label="Log Out"
            onClick={() => setSelectedTab(logOut)}
            selected={selectedTab === logOut}
          >
            <SignOutIcon color={iconColor(selectedTab === logOut)} />
          </MenuItem>
        </Menu>
      </SidebarNav>
      {
        (() => {
          switch (selectedTab) {
            case configuration: // TODO: handle these pages/actions
            case manage:
            case logOut: 
            default: // glossary
              return <EventGlossary />
          }
        })()
      }
    </div>
  );
};

export default EventDashboard;
