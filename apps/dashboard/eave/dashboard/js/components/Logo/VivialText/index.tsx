import { styled } from "@mui/material";
import React from "react";

import { colors } from "../../../theme/colors";
import { fontFamilies } from "../../../theme/fonts";

const Container = styled("div")(() => ({
  display: "inline-block",
  textAlign: "center",
  fontFamily: fontFamilies.quicksand,
  fontSize: "25.594px",
  fontStyle: "normal",
  fontWeight: 600,
  lineHeight: "normal",
  background: `linear-gradient(180deg, ${colors.vivialYellow} 21.67%, #F4AB70 127.33%)`,
  backgroundClip: "text",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
}));

const VivialText = () => {
  return <Container>vivial</Container>;
};

export default VivialText;
