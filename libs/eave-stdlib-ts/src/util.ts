export function redact(str: string | undefined): string | undefined {
  if (str === undefined) {
    return undefined;
  }

  const strlen = str.length;
  if (strlen <= 8) {
    return `[redacted ${strlen} chars]`;
  }

  return `${str.slice(0, 4)}[redacted ${strlen - 8} chars]${str.slice(-4)}`;
}
