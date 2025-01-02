import { useEffect, useState } from "react";

const MAX_MOBILE_WIDTH = 900; // from media-query breakpoint Medium

export const useMobile = () => {
  const [width, setWidth] = useState<number>(window.innerWidth);

  function handleWindowSizeChange() {
    setWidth(window.innerWidth);
  }
  useEffect(() => {
    window.addEventListener("resize", handleWindowSizeChange);
    return () => {
      window.removeEventListener("resize", handleWindowSizeChange);
    };
  }, []);

  return width <= MAX_MOBILE_WIDTH;
};
