// @ts-check
import React from "react";

import SidebarNav from "../SidebarNav/index.jsx";
import Menu from "../SidebarNav/Menu/index.jsx";
import MenuItem from "../SidebarNav/MenuItem/index.jsx";
import ExpandIcon from "../Icons/ExpandIcon.jsx";


const EventDashboard = () => {
  return (
    <SidebarNav>
      <Menu>
        <MenuItem icon={<ExpandIcon />} label="example" />
      </Menu>
    </SidebarNav>
  );
};

export default EventDashboard;