import { type NavigationState } from "$eave-dashboard/js/routes";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const location = useLocation();
  const { pathname } = location;
  const state = location.state as NavigationState | undefined | null;

  useEffect(() => {
    /**
     * setTimeout is used to mitigate race conditions.
     * window.scrollTo(0, 1) suppresses the search bar on Safari mobile when scrolling to top.
     */
    const scrollBehavior = state?.scrollBehavior;
    setTimeout(() => {
      window.scrollTo({ top: 0, left: 0, behavior: scrollBehavior });
    }, 10);
  }, [pathname]);
  return null;
};

export default ScrollToTop;
