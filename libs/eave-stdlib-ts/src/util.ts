export function redact(str: string | undefined): string | undefined {
  if (str === undefined) {
    return undefined;
  }
  if (str.length <= 8) {
    return '(redacted)';
  }

  return `${str.slice(0, 4)}..(redacted)..${str.slice(-4)}`;
}
