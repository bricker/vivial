import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    /**
     * setTimeout is used to mitigate race conditions.
     * window.scrollTo(0, 1) hides the search bar on Safari mobile when scrolling to top.
     */
    setTimeout(() => window.scrollTo(0, 1), 10);
  }, [pathname]);
  return null;
};

export default ScrollToTop;
