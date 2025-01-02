export function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function numWithEnglishSuffix(num: number) {
  const strnum = String(num)
  if (strnum.endsWith("11") || strnum.endsWith("12") || strnum.endsWith("13") || strnum.endsWith("4") || strnum.endsWith("5") || strnum.endsWith("6") || strnum.endsWith("7") || strnum.endsWith("8") || strnum.endsWith("9") || strnum.endsWith("0")) {
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
