import assert from "node:assert";

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

export function enumCases<O extends object>(
  obj: O,
): Array<NonNullable<O[keyof O]>> {
  return Object.keys(obj).reduce((acc, key, _) => {
    const candidateCase = obj[key as keyof typeof obj];
    // only add the enum case named keys (i.e. not numbers)
    // so exclude obj keys that dont get parsed to NaN
    if (candidateCase && Number.isNaN(parseInt(key, 10))) {
      acc.push(candidateCase);
    }
    return acc;
  }, Array<NonNullable<O[keyof O]>>());
}

export function xor(a: any, b: any): boolean {
  return !!a !== !!b;
}

export function normalizeExtName(extName: string): string {
  // quality-of-life (also to prevent bugs): Accept extension with or without leading dot
  if (extName.at(0) === ".") {
    return extName;
  } else {
    return `.${extName}`;
  }
}

export function assertPresence<T>(v: T | undefined | null, msg?: string): asserts v is T {
  assert(v !== undefined, msg || "Unexpected undefined value");
  assert(v !== null, msg || "Unexpected null value");
}

export function titleize(str: string) {
  return str.split(" ").filter((s) => s.length > 0).map((s) => s.at(0)!.toUpperCase() + s.slice(1)).join(" ");
}

export function underscoreify(str: string) {
  return str.replace(/[^a-zA-Z0-9]/g, "_").toLowerCase();
}