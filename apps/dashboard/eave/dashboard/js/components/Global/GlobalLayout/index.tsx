import React from "react";
import { Outlet } from "react-router-dom";

import { styled } from "@mui/material";
import Box, { BoxProps } from "@mui/material/Box";

import GlobalFooter from "../GlobalFooter";
import GlobalHeader from "../GlobalHeader";

const LayoutContainer = styled(Box)<BoxProps>(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  height: "100vh",
  overflowX: "hidden",
  overflowY: "scroll",
}));

const MainContent = styled("main")(() => ({
  flex: "1 1 auto",
}));

const GlobalLayout = () => {
  return (
    <LayoutContainer>
      <GlobalHeader />
      <MainContent>
        <Outlet />
      </MainContent>
      <GlobalFooter />
    </LayoutContainer>
  );
};

export default GlobalLayout;
