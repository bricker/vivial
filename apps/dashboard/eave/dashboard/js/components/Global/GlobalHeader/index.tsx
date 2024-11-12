import { styled } from "@mui/material";
import React from "react";

const Header = styled("header")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  flex: "0 0 60px",
  [theme.breakpoints.up("md")]: {
    flex: "0 0 88px",
  },
}));

const GlobalHeader = () => {
  return <Header>GLOBAL HEADER</Header>;
};

export default GlobalHeader;
