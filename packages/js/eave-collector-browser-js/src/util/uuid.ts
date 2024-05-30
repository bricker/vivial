// Copied from https://github.com/uuidjs/uuid/blob/main/src/stringify.js
// This is done for performance. Calling `rnds[i].toString(16)` is cleaner but has more runtime overhead.
const byteToHex: string[] = [];
for (let i = 0; i < 256; ++i) {
  byteToHex.push((i + 0x100).toString(16).slice(1));
}

/**
 * Generates a UUID (Universally Unique Identifier) using the v4 variant.
 * Prefers crypto.randomUUID when available. Otherwise, builds the UUID manually.
 *
 * @returns a randomly generated UUID.
 */
export function uuidv4(): string {
  // https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID
  // crypto.randomUUID is only available in secure contexts (eg https).
  if (crypto.randomUUID !== undefined) {
    return crypto.randomUUID();
  } else {
    // Copied from https://github.com/uuidjs/uuid/blob/main/src/v4.js
    // This is necessary when running in non-secure contexts.
    const rnds = new Uint8Array(16); // # of random values to pre-allocate
    crypto.getRandomValues(rnds); // modifies the array in-place

    // The following lines are ts-ignore'd because Typescript can't guarantee the length of the rnds array.
    // But we're pretty sure the length is 16. This function should _always_ return a valid UUID, so checking for undefined is useless.

    // Per 4.4, set bits for version and `clock_seq_hi_and_reserved`

    // @ts-ignore: see above
    rnds[6] = (rnds[6] & 0x0f) | 0x40;

    // @ts-ignore: see above
    rnds[8] = (rnds[8] & 0x3f) | 0x80;

    // prettier-ignore
    return (
      // @ts-ignore: see above
      byteToHex[rnds[0]] + byteToHex[rnds[1]] + byteToHex[rnds[2]] + byteToHex[rnds[3]] +
      "-" +
      // @ts-ignore: see above
      byteToHex[rnds[4]] + byteToHex[rnds[5]] +
      "-" +
      // @ts-ignore: see above
      byteToHex[rnds[6]] + byteToHex[rnds[7]] +
      "-" +
      // @ts-ignore: see above
      byteToHex[rnds[8]] + byteToHex[rnds[9]] +
      "-" +
      // @ts-ignore: see above
      byteToHex[rnds[10]] + byteToHex[rnds[11]] + byteToHex[rnds[12]] + byteToHex[rnds[13]] + byteToHex[rnds[14]] + byteToHex[rnds[15]]
    ).toLowerCase();
  }
}
