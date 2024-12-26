import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    setTimeout(() => window.scroll({ top: -1, left: 0, behavior: "instant" }), 10); // FIXME: sad race condition hack :(
  }, [pathname]);
  return null;
};

export default ScrollToTop;
