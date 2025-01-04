import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";

export enum HeaderHeight {
  Mobile = 60,
  Desktop = 88,
}

export enum HeaderVariant {
  Static,
  Sticky,
}

const Header = styled("header", { shouldForwardProp: (prop) => prop !== "variant" })<{ variant?: HeaderVariant }>(
  ({ theme, variant = HeaderVariant.Static }) => ({
    position: (() => {
      switch (variant) {
        case HeaderVariant.Sticky:
          return "sticky";
        default:
          return "static";
      }
    })(),
    top: 0,
    zIndex: 2,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 24px",
    backgroundColor: theme.palette.background.paper,
    flex: `0 0 ${HeaderHeight.Mobile}px`,
    [theme.breakpoints.up(Breakpoint.Medium)]: {
      flex: `0 0 ${HeaderHeight.Desktop}px`,
    },
  }),
);

export default Header;
