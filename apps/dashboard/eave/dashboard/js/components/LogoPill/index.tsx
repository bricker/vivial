import { colors } from "$eave-dashboard/js/theme/colors";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { styled } from "@mui/material";
import React from "react";

const LogoImage = styled("img")<{ width: number }>(({ width }) => ({
  height: "auto",
  width,
}));

const LogoContainer = styled("div")<{ backgroundColor: string }>(({ backgroundColor }) => ({
  borderRadius: 10,
  width: 136,
  minWidth: 136, // Ensures 136 width as flex item.
  height: 40,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  backgroundColor,
}));

export interface LogoPillAttributes {
  backgroundColor: string;
  alt: string;
  logoUri: string;
  logoWidth: number;
}

export const logos: { [key: string]: LogoPillAttributes } = {
  vivial: {
    logoUri: imageUrl("vivial-word-logo.png"),
    alt: "Vivial",
    backgroundColor: colors.vivialYellow,
    logoWidth: 65,
  },
  opentable: {
    logoUri: imageUrl("opentable-logo.png"),
    alt: "Opentable",
    backgroundColor: "#DA3644",
    logoWidth: 91.4,
  },
  eventbrite: {
    logoUri: imageUrl("eventbrite-logo.png"),
    alt: "Eventbrite",
    backgroundColor: "#F05537",
    logoWidth: 83.7,
  },
};

const LogoPill = ({ attrs: { backgroundColor, alt, logoUri, logoWidth } }: { attrs: LogoPillAttributes }) => {
  return (
    <LogoContainer backgroundColor={backgroundColor}>
      <LogoImage alt={alt} src={logoUri} width={logoWidth} />
    </LogoContainer>
  );
};

export default LogoPill;
