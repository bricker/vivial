/**
 * In CSS, rem stands for "root em". It is a unit of measurement used to define
 * sizes relative to the font size set on the root element of the document.
 *
 * In other words, it is a font size relative to the root element of the document.
 * This is useful for users who set a custom default browser font-size.
 */
export function rem(pixelFontSize: number) {
  const rootFontSize = parseFloat(window.getComputedStyle(document.documentElement).fontSize) || 16;
  return `${pixelFontSize / rootFontSize}rem`;
}
