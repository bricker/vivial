import { colors } from "$eave-dashboard/js/theme/colors";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { styled } from "@mui/material";
import React from "react";

const LogoImage = styled("img")(() => ({
  height: "100%",
  maxWidth: "100%",
}));

const LogoContainer = styled("div")<{ padding: number; backgroundColor: string }>(({ padding, backgroundColor }) => ({
  borderRadius: 10,
  width: "40%",
  minWidth: "40%",
  aspectRatio: 3.4,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  backgroundColor,
  padding,
}));

export interface LogoPillAttributes {
  backgroundColor: string;
  padding: number;
  alt: string;
  logoUri: string;
}

export const logos: { [key: string]: LogoPillAttributes } = {
  vivial: {
    logoUri: imageUrl("vivial-word-logo.png"),
    alt: "Vivial",
    backgroundColor: colors.vivialYellow,
    padding: 11,
  },
  opentable: {
    logoUri: imageUrl("opentable-logo.png"),
    alt: "Opentable",
    backgroundColor: "#DA3644",
    padding: 8,
  },
  eventbrite: {
    logoUri: imageUrl("eventbrite-logo.png"),
    alt: "Eventbrite",
    backgroundColor: "#F05537",
    padding: 12,
  },
};

const LogoPill = ({ attrs: { backgroundColor, padding, alt, logoUri } }: { attrs: LogoPillAttributes }) => {
  return (
    <LogoContainer backgroundColor={backgroundColor} padding={padding}>
      <LogoImage alt={alt} src={logoUri} />
    </LogoContainer>
  );
};

export default LogoPill;
