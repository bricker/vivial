import { useEffect, useState } from "react";

export enum MediaQuery {
  ExtraSmall = "@media (min-width: 0px)",
  Small = "@media (min-width: 600px)",
  Medium = "@media (min-width: 900px)",
  Large = "@media (min-width: 1200px)",
  ExtraLarge = "@media (min-width: 1536px)",
}

export enum Breakpoint {
  Unset = "",
  ExtraSmall = "xs",
  Small = "sm",
  Medium = "md",
  Large = "lg",
  ExtraLarge = "xl",
}

export function isDesktop(breakpoint: Breakpoint) {
  return [Breakpoint.Medium, Breakpoint.Large, Breakpoint.ExtraLarge].includes(breakpoint);
}

/**
 * Helper to determine which MUI Breakpoint the user's viewport is at.
 *
 * Returns:
 *   • "xs" (extra-small: 0px)
 *   • "sm" (small: 600px")
 *   • "md" (medium: 900px)
 *   • "lg" large: 1200px
 *   • "xl" (extra-large: 1536px)
 *
 * Reference: https://mui.com/material-ui/customization/breakpoints/
 */
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState(Breakpoint.Unset);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  const handleResize = () => {
    setWindowWidth(window.innerWidth);
  };

  useEffect(() => {
    window.addEventListener("resize", handleResize);
    handleResize();
    if (windowWidth < 600) {
      setBreakpoint(Breakpoint.ExtraSmall);
      return;
    }
    if (windowWidth < 900) {
      setBreakpoint(Breakpoint.Small);
      return;
    }
    if (windowWidth < 1200) {
      setBreakpoint(Breakpoint.Medium);
      return;
    }
    if (windowWidth < 1536) {
      setBreakpoint(Breakpoint.Large);
      return;
    }
    setBreakpoint(Breakpoint.ExtraLarge);
    return () => window.removeEventListener("resize", handleResize);
  }, [windowWidth]);

  return breakpoint;
};
