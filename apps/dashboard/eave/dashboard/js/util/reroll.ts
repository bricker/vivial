import { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { CookieId, RerollCookie } from "../types/cookie";
import { in24Hours } from "./date";

export const MAX_REROLLS = 10;

export function useReroll(): [number, () => void] {
  const [rerolls, setRerolls] = useState<number>(0);
  const [cookies, setCookie] = useCookies([CookieId.Reroll]);
  const rerollCookie = cookies[CookieId.Reroll] as RerollCookie;

  const updateCookie = (rerollsUpdate: number, expires: Date) => {
    setCookie(CookieId.Reroll, { rerolls: rerollsUpdate, expires }, { expires, path: "/" });
  };

  const rerolled = () => {
    if (rerollCookie) {
      updateCookie(rerollCookie.rerolls + 1, new Date(rerollCookie.expires));
    } else {
      updateCookie(1, in24Hours());
    }
  };

  useEffect(() => {
    if (rerollCookie) {
      setRerolls(rerollCookie.rerolls);
    }
  }, [rerollCookie]);

  return [rerolls, rerolled];
}
