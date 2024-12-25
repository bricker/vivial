import { createTheme } from "@mui/material";
import { colors } from "./colors";
import { fontFamilies } from "./fonts";
import { MediaQuery } from "./helpers/breakpoint";
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
      primary: colors.fieldBackground.primary,
      secondary: colors.fieldBackground.secondary,
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
      fontSize: rem(40),
      lineHeight: rem(50),
      fontWeight: 600,
      [MediaQuery.Medium]: {
        fontSize: rem(59.475),
        lineHeight: rem(74),
      },
    },
    h2: {
      fontFamily: fontFamilies.quicksand,
      color: colors.vivialYellow,
      fontSize: rem(36),
      lineHeight: rem(45),
      fontWeight: 600,
    },
    h3: {
      fontFamily: fontFamilies.quicksand,
      color: colors.vivialYellow,
      fontSize: rem(28),
      lineHeight: rem(35),
      fontWeight: 600,
    },
    h4: {
      color: colors.vivialYellow,
      fontSize: rem(20),
      fontFamily: fontFamilies.quicksand,
      fontWeight: 500,
    },
    h5: {
      color: colors.pureWhite,
      fontSize: rem(16),
      lineHeight: rem(20),
      fontFamily: fontFamilies.quicksand,
      fontWeight: 700,
    },
    subtitle1: {
      fontSize: rem(14),
      lineHeight: rem(20.513),
      fontWeight: 400,
      [MediaQuery.Medium]: {
        fontSize: rem(18.586),
        lineHeight: rem(22),
      },
    },
    subtitle2: {
      fontSize: rem(16),
      lineHeight: rem(19),
      fontWeight: 400,
    },
    body1: {
      fontSize: rem(14),
      lineHeight: rem(22),
    },
    body2: {
      fontSize: rem(12),
      fontWeight: 500,
    },
    button: {
      fontFamily: fontFamilies.quicksand,
      fontSize: rem(16),
      lineHeight: rem(20),
      fontWeight: 600,
      textTransform: "none",
      letterSpacing: "normal",
    },
  },
});
