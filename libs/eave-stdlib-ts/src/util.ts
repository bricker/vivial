import assert from "node:assert";

/**
 * Redacts a portion of a string, replacing it with a '[redacted]' message and the number of redacted characters.
 * If the string is shorter than or equal to the specified length, the entire string is redacted.
 * If the string is longer than the specified length, the redaction occurs in the middle of the string.
 *
 * @param str - The string to be redacted. If not provided, the function returns undefined.
 * @param length - The length of the string to remain unredacted. Defaults to 8.
 * @returns The redacted string, or undefined if no string was provided.
 */
export function redact(str?: string, length = 8): string | undefined {
  if (str === undefined) {
    return undefined;
  }

  const strlen = str.length;
  if (strlen <= length) {
    return `[redacted ${strlen} chars]`;
  }

  // This effectively turns an odd number into an even number, so we don't have to deal with floats
  const slicelen = Math.floor(length / 2);
  return `${str.slice(0, slicelen)}[redacted ${
    strlen - slicelen * 2
  } chars]${str.slice(-slicelen)}`;
}

/**
 * Returns an array of non-nullable values from the provided object, excluding keys that can be parsed to numbers.
 *
 * @param obj - The object to extract values from.
 * @returns An array of non-nullable values from the object.
 *
 * @template O - The type of the object.
 */
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

/**
 * Performs a logical XOR operation on two values.
 *
 * @param a - The first value to compare.
 * @param b - The second value to compare.
 * @returns A boolean indicating whether exactly one of the inputs is truthy.
 */
export function xor(a: any, b: any): boolean {
  return !!a !== !!b;
}

/**
 * Normalizes the extension name by ensuring it starts with a dot.
 * If the input extension name already starts with a dot, it is returned as is.
 * Otherwise, a dot is prepended to the extension name.
 *
 * @param extName - The extension name to normalize.
 * @returns The normalized extension name.
 */
export function normalizeExtName(extName: string): string {
  // quality-of-life (also to prevent bugs): Accept extension with or without leading dot
  if (extName.at(0) === ".") {
    return extName;
  } else {
    return `.${extName}`;
  }
}

/**
 * Asserts that a value is neither undefined nor null.
 * Throws an error if the value is undefined or null.
 *
 * @template T - The type of the value.
 * @param {T | undefined | null} v - The value to check.
 * @param {string} [msg] - Optional custom error message.
 * @throws {AssertionError} If the value is undefined or null.
 */
export function assertPresence<T>(
  v: T | undefined | null,
  msg?: string,
): asserts v is T {
  assert(v !== undefined, msg || "Unexpected undefined value");
  assert(v !== null, msg || "Unexpected null value");
}

/**
 * Transforms a string into title case.
 * Splits the input string into words, capitalizes the first letter of each word, and then joins them back together.
 *
 * @param str - The string to be transformed into title case.
 * @returns The input string converted into title case.
 */
export function titleize(str: string) {
  return str
    .split(" ")
    .filter((s) => s.length > 0)
    .map((s) => s.at(0)!.toUpperCase() + s.slice(1))
    .join(" ");
}

/**
 * Replaces all non-alphanumeric characters in a string with underscores and converts the string to lowercase.
 *
 * @param {string} str - The string to be processed.
 * @returns {string} The processed string with all non-alphanumeric characters replaced by underscores and converted to lowercase.
 */
export function underscoreify(str: string) {
  return str.replace(/[^a-zA-Z0-9]/g, "_").toLowerCase();
}
