import path from "node:path";
import extensionMap from "./generated/languages.json" assert { type: "json" };
import { normalizeExtName } from "../util.js";

export enum ProgrammingLanguage {
  javascript = "javascript",
  typescript = "typescript",
  rust = "rust",
  c = "c",
  go = "go",
  java = "java",
  kotlin = "kotlin",
  ruby = "ruby",
  cpp = "cpp",
  php = "php",
  swift = "swift",
  csharp = "csharp",
}

/**
 * Converts string to enum case. Necessary to translate language name strings
 * with special characters to the correct enum case.
 * @param lang string to convert, if possible
 * @return ProgrammingLanguage enum case, or undefined if `lang` is not a case
 */
export function stringToProgrammingLanguage(
  lang: string,
): ProgrammingLanguage | undefined {
  const language = lang.toLowerCase();
  // handle languages w/ special characters in name separately
  switch (language) {
    case "c++":
      return ProgrammingLanguage.cpp;
    case "c#":
      return ProgrammingLanguage.csharp;
    default:
      return ProgrammingLanguage[language as keyof typeof ProgrammingLanguage];
  }
}

export function getProgrammingLanguageByExtension(
  extName: string,
): ProgrammingLanguage | undefined {
  extName = normalizeExtName(extName);
  const lang = extensionMap[extName as keyof typeof extensionMap];
  return lang ? stringToProgrammingLanguage(lang) : undefined;
}

export function getProgrammingLanguageByFilePathOrName(filePathOrName: string): ProgrammingLanguage | undefined {
  const extName = `${path.extname(filePathOrName).toLowerCase()}`;
  return getProgrammingLanguageByExtension(extName);
}

export function isSupportedProgrammingLanguage(extName: string): boolean {
  const lang = getProgrammingLanguageByExtension(extName);
  return lang !== undefined;
}
