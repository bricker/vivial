import GlossaryIcon from "$eave-dashboard/js/components/Icons/GlossaryIcon";
import GraphIcon from "$eave-dashboard/js/components/Icons/GraphIcon";
import SettingsCogIcon from "$eave-dashboard/js/components/Icons/SettingsCogIcon";
import SetupIcon from "$eave-dashboard/js/components/Icons/SetupIcon";
import SignOutIcon from "$eave-dashboard/js/components/Icons/SignOutIcon";
import TeamIcon from "$eave-dashboard/js/components/Icons/TeamIcon";
import SidebarNav from "$eave-dashboard/js/components/SidebarNav";
import Menu from "$eave-dashboard/js/components/SidebarNav/Menu";
import MenuItem from "$eave-dashboard/js/components/SidebarNav/MenuItem";
import { theme } from "$eave-dashboard/js/theme";
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  spacer: {
    flexGrow: 1,
  },
}));

function iconColor(isSelected: boolean): "white" | "black" {
  return isSelected ? "white" : "black";
}

const TabbedNav = () => {
  const location = useLocation();
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

  const { classes } = makeClasses();

  return (
    <SidebarNav hamburger={usingMobileLayout}>
      <Menu>
        <MenuItem label="Setup" to="/setup" selected={location.pathname === "/setup"} expanded={usingMobileLayout}>
          <SetupIcon color={iconColor(location.pathname === "/setup")} />
        </MenuItem>

        <MenuItem
          label="Insights"
          to="/insights"
          selected={location.pathname === "/insights"}
          expanded={usingMobileLayout}
        >
          <GraphIcon color={iconColor(location.pathname === "/insights")} />
        </MenuItem>

        <MenuItem
          label="Event Glossary"
          to="/glossary"
          selected={location.pathname === "/glossary"}
          expanded={usingMobileLayout}
        >
          <GlossaryIcon color={iconColor(location.pathname === "/glossary")} />
        </MenuItem>

        {!usingMobileLayout && <div className={classes.spacer}></div>}

        <MenuItem
          label="Settings"
          to="/settings"
          selected={location.pathname === "/settings"}
          expanded={usingMobileLayout}
        >
          <SettingsCogIcon color={iconColor(location.pathname === "/settings")} />
        </MenuItem>

        <MenuItem
          label="Team Management"
          to="/team"
          selected={location.pathname === "/team"}
          expanded={usingMobileLayout}
        >
          <TeamIcon color={iconColor(location.pathname === "/team")} />
        </MenuItem>

        <MenuItem label="Log Out" to="/logout" reloadDocument={true} selected={false} expanded={usingMobileLayout}>
          <SignOutIcon color={iconColor(false)} />
        </MenuItem>
      </Menu>
    </SidebarNav>
  );
};

export default TabbedNav;
