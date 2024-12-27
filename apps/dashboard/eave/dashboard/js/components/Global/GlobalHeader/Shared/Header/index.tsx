import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";
import { styled } from "@mui/material";

export enum HeaderHeight {
  Mobile = 60,
  Desktop = 88,
}

const Header = styled("header")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "0 24px",
  backgroundColor: theme.palette.background.paper,
  opacity: 1,
  flex: `0 0 ${HeaderHeight.Mobile}px`,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    flex: `0 0 ${HeaderHeight.Desktop}px`,
  },
}));

export default Header;
