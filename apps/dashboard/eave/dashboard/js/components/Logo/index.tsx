import React, { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { styled } from "@mui/material";
import Button from "@mui/material/Button";

import { AppRoute } from "$eave-dashboard/js/routes";
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

interface VivialLogoProps {
  hideText?: boolean;
}

const VivialLogo = ({ hideText }: VivialLogoProps) => {
  const navigate = useNavigate();
  const handleClick = useCallback(() => {
    navigate(AppRoute.root);
  }, []);

  return (
    <LogoButton onClick={handleClick}>
      <VivialIcon />
      {!hideText && (
        <TextContainer>
          <VivialText />
        </TextContainer>
      )}
    </LogoButton>
  );
};

export default VivialLogo;
