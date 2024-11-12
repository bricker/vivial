import { styled } from "@mui/material";
import React from "react";

const Footer = styled("footer")(({ theme }) => ({
  flex: "0 0 140px",
  [theme.breakpoints.up("md")]: {
    flex: "0 0 80px",
  },
}));

const GlobalFooter = () => {
  return <Footer>GLOBAL FOOTER</Footer>;
};

export default GlobalFooter;
