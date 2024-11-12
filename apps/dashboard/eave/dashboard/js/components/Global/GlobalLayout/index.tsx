import React from "react";
import { Outlet } from "react-router-dom";

import Box, { BoxProps } from "@mui/material/Box";
import { styled } from "@mui/material/styles";

import GlobalFooter from "../GlobalFooter";
import GlobalHeader from "../GlobalHeader";

const Container = styled(Box)<BoxProps>(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  minHeight: "100vh",
}));

const MainContent = styled("main")(() => ({
  flex: "1 1 auto",
}));

const GlobalLayout = () => {
  return (
    <Container>
      <GlobalHeader />
      <MainContent>
        <Outlet />
      </MainContent>
      <GlobalFooter />
    </Container>
  );
};

export default GlobalLayout;
