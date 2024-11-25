import { createTheme } from "@mui/material";
import { colors } from "./colors";
import { fontFamilies } from "./fonts";
import { rem } from "./helpers/rem";

// export interface EaveHeaderStyle {
//   height: number;
//   marginBottom: number;
//   md: {
//     height: number;
//     marginBottom: number;
//   };
// }

// export interface EaveFooterStyle {
//   height: number;
// }

// declare module "@mui/material/styles" {
//   interface BreakpointOverrides {
//     xs: true;
//     sm: true;
//     md: true;
//     lg: true;
//     xl: true;
//     thin: true;
//   }

//   interface TypeBackground {
//     main: string;
//     light: string;
//     contrastText: string;
//   }

//   interface Palette {
//     tertiary: PaletteColor;
//     disabled: PaletteColor;
//   }

//   interface PaletteOptions {
//     tertiary?: PaletteColorOptions;
//     disabled?: PaletteColorOptions;
//   }

//   interface Theme {
//     header: EaveHeaderStyle;
//     footer: EaveFooterStyle;
//   }

//   interface ThemeOptions {
//     header?: Partial<EaveHeaderStyle>;
//     footer?: Partial<EaveFooterStyle>;
//   }
// }

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
      500: colors.grey[500],
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
    subtitle1: {
      fontSize: rem("14px"),
      lineHeight: rem("20.5px"),
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
