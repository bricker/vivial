export function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function numWithEnglishSuffix(num: number) {
  const strnum = String(num)
  if (["11", "12", "13", "0", "4", "5", "6", "7", "8", "9"].some((n) => strnum.endsWith(n))) {
    return `${num}th`;
  } else if (strnum.endsWith("1")) {
    return `${num}st`;
  } else if (strnum.endsWith("2")) {
    return `${num}nd`;
  } else if (strnum.endsWith("3")) {
    return `${num}rd`;
  } else {
    return `${num}`;
  }
}
