// @ts-check
import React, { useState } from "react";
import * as Types from "../../types.js"; // eslint-disable-line no-unused-vars
import { makeStyles } from "@material-ui/styles";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({}));
// TODO: css

// TODO: if mobile, collaps to top-right burger menue
const SidebarNav = ({/** @type {React.ReactNode} */ children}) => {
  const [selectedTab, setSelectedTab] = useState('todo default');
  const classes = makeClasses();

  return (
    <div>
      {children}
    </div>
  );
};

export default SidebarNav;