/**
 * These colors map to the colors in the Vivial Figma Design files.
 * https://www.figma.com/design/lehDvAyzQZLEsWADXrtM4m/Final-Designs?node-id=0-1&t=4o5pYaazPBOC0sIy-1
 */
export const colors = {
  whiteText: "#D9D9D9",
  vivialYellow: "#E6F025",
  fieldBackground: {
    primary: "#312B2C",
    secondary: "#121212",
  },
  secondaryButtonCTA: "#434343",
  lightPurpleAccent: "#CCACEC",
  lightOrangeAccent: "#FCC3A3",
  lightPinkAccent: "#FF81B5",
  brightPinkAccent: "#D2286E",
  darkPurpleAccent: "#6D208C",
  mediumPurpleAccent: "#AF83FD",
  brightOrangeAccent: "#D1591B",
  midGreySecondaryField: "#ABABAB",
  pureWhite: "#FFFFFF",
  pureBlack: "#000000",
  errorRed: "#FF3B3B",
  passingGreen: "#54FF68",
  almostBlackBG: "#1E1E1E",
  grey: {
    300: "#C3C1BC",
    400: "#B3B3B3",
    500: "#8C8C8C",
    800: "#434343",
    900: "#332C2D",
  },
};

type Tuple<T, N extends number> = N extends N ? (number extends N ? T[] : _TupleOf<T, N, []>) : never;
type _TupleOf<T, N extends number, R extends unknown[]> = R["length"] extends N ? R : _TupleOf<T, N, [T, ...R]>;

/**
 * Break a hex color string into its numeric RGB components.
 * @param hex hex color string with leading # and 6 characters long
 * @return list of length 3, representing the R, G, and B color components of `hex`, in that order.
 */
export function hexToRGB(hex: string): Tuple<number, 3> {
  if (hex.length !== 7) {
    // fallback to return something valid
    return [0, 0, 0];
  }
  return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)].map(
    (component) => (isNaN(component) ? 0 : component),
  ) as Tuple<number, 3>;
}
