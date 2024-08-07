export const COOKIE_PREFIX = "quizapp.";

export function getAllCookies(): URLSearchParams {
  const urlParamifiedCookies = document.cookie.replace(/; */g, "&");
  const cookies = new URLSearchParams(urlParamifiedCookies);
  return cookies;
}

export function getCookie(name: string): string | null {
  const cookies = getAllCookies();
  return cookies.get(name);
}

export function setCookie({ name, value, maxAge = 2592000 }: { name: string; value: string; maxAge?: number }) {
  document.cookie = `${name}=${value}; max-age=${maxAge}`;
}

export function deleteCookie({ name }: { name: string }) {
  setCookie({ name, value: "", maxAge: 0 });
}

export function deleteAllCookies() {
  const allCookies = getAllCookies();
  for (const [name, _] of allCookies) {
    if (name.startsWith(COOKIE_PREFIX)) {
      deleteCookie({ name });
    }
  }
}
