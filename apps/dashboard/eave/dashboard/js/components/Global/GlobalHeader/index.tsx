import { styled } from "@mui/material";
import React from "react";

import VivialLogo from "../../Logo";

const Header = styled("header")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  flex: "0 0 60px",
  [theme.breakpoints.up("md")]: {
    flex: "0 0 88px",
  },
}));

const GlobalHeader = () => {
  return (
    <Header>
      <VivialLogo />
    </Header>
  );
};

export default GlobalHeader;
