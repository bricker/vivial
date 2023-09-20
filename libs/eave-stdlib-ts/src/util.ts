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

export function enumCases<O extends object>(obj: O): Array<NonNullable<O[keyof O]>> {
  return Object.keys(obj).reduce((acc, key, _) => {
    const candidateCase = obj[key as keyof typeof obj];
    if (candidateCase && Number.isNaN(key)) {
      acc.push(candidateCase);
    }
    return acc;
  }, Array<NonNullable<O[keyof O]>>());
}
