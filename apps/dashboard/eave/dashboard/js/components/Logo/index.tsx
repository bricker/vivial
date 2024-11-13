import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { styled } from "@mui/material";
import Button from "@mui/material/Button";

import VivialIcon from "./VivialIcon";
import VivialText from "./VivialText";

const LogoButton = styled(Button)(() => ({
  display: "flex",
  alignItems: "center",
  padding: 0,
}));

const TextContainer = styled("div")(() => ({
  marginLeft: 8,
}));

const VivialLogo = () => {
  const navigate = useNavigate();
  const handleClick = useCallback(() => {
    navigate("/")
  }, []);

  return (
    <LogoButton onClick={handleClick}>
      <VivialIcon />
      <TextContainer>
        <VivialText />
      </TextContainer>
    </LogoButton>
  );
};

export default VivialLogo;
