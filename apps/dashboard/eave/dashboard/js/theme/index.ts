import { createTheme } from "@mui/material";
import { colors } from "./colors";
import { fontFamilies } from "./fonts";

/**
 * MaterialUI Custom Theme Overrides.
 * Default Theme: https://mui.com/material-ui/customization/default-theme/
 */
export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: colors.vivialYellow,
    },
    text: {
      primary: colors.whiteText,
      secondary: colors.midGreySecondaryField,
    },
    background: {
      paper: colors.almostBlackBG,
      default: colors.pureBlack,
    },
    grey: {
      500: colors.grey[500],
    },
  },
  typography: {
    fontFamily: fontFamilies.inter,
    button: {
      textTransform: "none",
      letterSpacing: "normal",
    },
  },
});
