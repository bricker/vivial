import { styled } from "@mui/material";
import Button from "@mui/material/Button";
import React from "react";

import LogInButton from "../../Buttons/LogInButton";
import VivialLogo from "../../Logo";

const Header = styled("header")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "0 24px",
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
      <LogInButton />
    </Header>
  );
};

export default GlobalHeader;
