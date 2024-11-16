import "@mui/material";

declare module "@mui/material/styles" {
  interface PaletteOptions {
    field?: {
      background: string;
    };
    accent?: {
      1: string;
      2: string;
      3: string;
      4: string;
      5: string;
      6: string;
      7: string;
    };
  }
  interface Palette {
    field: {
      background: string;
    };
    accent?: {
      1: string;
      2: string;
      3: string;
      4: string;
      5: string;
      6: string;
      7: string;
    };
  }
}
