import { createTheme } from "@mui/material";
import { colors } from "./colors";

/**
 * MaterialUI Custom Theme Overrides.
 * Default Theme: https://mui.com/material-ui/customization/default-theme/
 */
export const theme = createTheme({
  palette: {
    mode: "dark",
    background: {
      paper: colors.almostBlackBG,
      default: colors.pureBlack,
    },
  },
});
