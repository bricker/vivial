import { styled } from "@mui/material";
import React from "react";

import VivialIcon from "./VivialIcon";
import VivialText from "./VivialText";

const LogoContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
}));

const TextContainer = styled("div")(() => ({
  marginLeft: 8.47,
}));

const VivialLogo = () => {
  return (
    <LogoContainer>
      <VivialIcon />
      <TextContainer>
        <VivialText />
      </TextContainer>
    </LogoContainer>
  );
};

export default VivialLogo;
