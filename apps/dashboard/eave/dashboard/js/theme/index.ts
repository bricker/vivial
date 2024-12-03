import { createTheme } from "@mui/material";
import { colors } from "./colors";
import { fontFamilies } from "./fonts";
import { rem } from "./helpers/rem";

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
    error: {
      main: colors.errorRed,
    },
    success: {
      main: colors.passingGreen,
    },
    accent: {
      1: colors.lightOrangeAccent,
      2: colors.lightPurpleAccent,
      3: colors.lightPinkAccent,
      4: colors.brightPinkAccent,
      5: colors.darkPurpleAccent,
      6: colors.mediumPurpleAccent,
      7: colors.brightOrangeAccent,
    },
    text: {
      primary: colors.whiteText,
      secondary: colors.midGreySecondaryField,
      disabled: colors.midGreySecondaryField,
    },
    field: {
      background: colors.fieldBackground,
    },
    background: {
      paper: colors.almostBlackBG,
      default: colors.pureBlack,
    },
    grey: {
      300: colors.grey[300],
      400: colors.grey[400],
      500: colors.grey[500],
      800: colors.grey[800],
      900: colors.grey[900],
    },
  },
  typography: {
    fontFamily: fontFamilies.inter,
    h1: {
      fontFamily: fontFamilies.quicksand,
      color: colors.vivialYellow,
      textTransform: "uppercase",
      fontSize: rem("40px"),
      lineHeight: rem("50px"),
      fontWeight: 600,
    },
    h2: {
      fontFamily: fontFamilies.quicksand,
      color: colors.vivialYellow,
      fontSize: rem("36px"),
      lineHeight: rem("45px"),
      fontWeight: 600,
    },
    h3: {
      fontFamily: fontFamilies.quicksand,
      color: colors.vivialYellow,
      fontSize: rem("28px"),
      lineHeight: rem("35px"),
      fontWeight: 600,
    },
    h4: {
      color: colors.vivialYellow,
      fontSize: rem("20px"),
      fontFamily: fontFamilies.quicksand,
      fontWeight: 500,
    },
    subtitle1: {
      fontSize: rem("14px"),
      lineHeight: rem("20.513px"),
      fontWeight: 400,
    },
    subtitle2: {
      fontSize: rem("16px"),
      lineHeight: rem("19px"),
      fontWeight: 400,
    },
    button: {
      fontFamily: fontFamilies.quicksand,
      fontSize: rem("16px"),
      lineHeight: rem("20px"),
      fontWeight: 600,
      textTransform: "none",
      letterSpacing: "normal",
    },
  },
});
