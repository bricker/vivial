import { PaletteColor, PaletteColorOptions, createTheme } from "@mui/material";

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
