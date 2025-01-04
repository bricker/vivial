import { isDesktop, useBreakpoint } from "../theme/helpers/breakpoint";

export const useMobile = () => {
  const breakpoint = useBreakpoint();
  return !isDesktop(breakpoint);
};
