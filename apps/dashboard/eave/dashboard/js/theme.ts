import { PaletteColor, PaletteColorOptions, createTheme } from "@mui/material";
import { makeStyles } from "tss-react/mui";

export interface EaveHeaderStyle {
  height: number;
  marginBottom: number;
  md: {
    height: number;
    marginBottom: number;
  };
}

export interface EaveFooterStyle {
  height: number;
}

export interface SidebarIcon {
  color?: string;
  width?: string;
  height?: string;
}

declare module "@mui/material/styles" {
  interface BreakpointOverrides {
    xs: true;
    sm: true;
    md: true;
    lg: true;
    xl: true;
    thin: true;
  }

  interface TypeBackground {
    main: string;
    light: string;
    contrastText: string;
  }

  interface Palette {
    tertiary: PaletteColor;
    disabled: PaletteColor;
  }

  interface PaletteOptions {
    tertiary?: PaletteColorOptions;
    disabled?: PaletteColorOptions;
  }

  interface Theme {
    header: EaveHeaderStyle;
    footer: EaveFooterStyle;
  }

  interface ThemeOptions {
    header?: Partial<EaveHeaderStyle>;
    footer?: Partial<EaveFooterStyle>;
  }
}

/**
 * Theme Defaults: https://mui.com/material-ui/customization/theming
 */
export const theme = createTheme({
  palette: {
    primary: {
      // yellow
      main: "#F4E346",
      light: "#F8ED87",
      dark: "#F1DA0E",
      contrastText: "#121212",
    },
    secondary: {
      // green
      main: "#13D491",
      light: "#14EBA0",
      dark: "#10BC80",
      contrastText: "#121212",
    },
    tertiary: {
      // blue
      main: "#01A6F7",
      light: "#1BB2FE",
      dark: "#0188CB",
      contrastText: "#FFFFFF",
    },
    error: {
      // red
      main: "#E03C6C",
    },
    background: {
      // black
      main: "#121212",
      light: "#363636",
      contrastText: "#FFFFFF",
    },
    disabled: {
      // gray
      main: "#9A9996",
      light: "#5E5C64",
      dark: "#9A9996",
    },
    // for now using as new theme
    success: {
      main: "#1980DF",
    },
  },
  typography: {
    fontFamily: ["DM Sans", "sans-serif"].join(","),
  },
  header: {
    height: 66,
    marginBottom: 28,
    md: {
      height: 110,
      marginBottom: 86,
    },
  },
  footer: {
    height: 70,
  },
  breakpoints: {
    values: {
      xs: 0,
      thin: 500,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
});

export const textStyles = makeStyles()((_theme) => ({
  display: {
    fontSize: 64,
    lineHeight: 1.1,
    [theme.breakpoints.down("md")]: {
      fontSize: 48,
    },
  },
  headerIII: {
    fontSize: 52,
    fontWeight: "normal",
    lineHeight: 1.1,
    margin: 0,
  },
  headerII: {
    fontSize: 36,
    fontWeight: "normal",
    margin: 0,
    [theme.breakpoints.down("md")]: {
      fontSize: 24,
    },
  },
  header: {
    fontSize: 24,
    margin: 0,
    fontWeight: "normal",
    lineHeight: 1.25,
  },
  subHeader: {
    fontSize: 20,
    fontWeight: "normal",
    margin: 0,
  },
  body: {
    fontSize: 20,
    margin: 0,
    [theme.breakpoints.down("md")]: {
      fontSize: 18,
    },
  },
  bold: {
    fontWeight: "bold",
  },
  gray: {
    color: "#7D7D7D",
  },
  error: {
    color: _theme.palette.error.main,
    padding: "0px 30px",
    textAlign: "center",
    fontSize: "26px",
  },
}));

export const buttonStyles = makeStyles()((_theme) => ({
  default: {
    backgroundColor: "#E8F4FF",
    color: _theme.palette.success.main,
    borderRadius: 4,
    margin: 0,
    padding: "8px 8px",
    height: "fit-content",
    border: "1px solid #1980DF",
    fontSize: 16,
    fontWeight: "bold",
    cursor: "pointer",
    width: "150px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  invisible: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "transparent",
    border: "0px",
  },
  darkBlue: {
    backgroundColor: "#1980DF",
    cursor: "pointer",
    color: "white",
    borderRadius: 10,
    margin: 0,
    padding: "16px 32px",
    height: "fit-content",
    border: "1px solid #1980DF",
    fontSize: 20,
    fontWeight: "bold",
  },

  disabled: {
    opacity: "50%",
  },
}));

export const uiStyles = makeStyles()((_theme) => ({
  loadingContainer: {
    position: "fixed",
    width: "100%",
    height: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255)",
    zIndex: 100,
  },
  opaque: {
    backgroundColor: "rgba(255, 255, 255, 0.5)",
    cursor: "pointer",
  },
}));
