import extensionMap from './languages.json';

export enum ProgrammingLanguage {
  javascript = 'javascript',
  typescript = 'typescript',
  rust = 'rust',
  c = 'c',
  go = 'go',
  java = 'java',
  kotlin = 'kotlin',
  ruby = 'ruby',
  cpp = 'cpp',
  php = 'php',
  swift = 'swift',
  csharp = 'csharp',
}

/**
 * Converts string to enum case. Necessary to translate language name strings
 * with special characters to the correct enum case.
 * @param lang string to convert, if possible
 * @return ProgrammingLanguage enum case, or undefined if `lang` is not a case
 */
export function stringToProgrammingLanguage(lang: string): ProgrammingLanguage | undefined {
  const language = lang.toLowerCase();
  // handle languages w/ special characters in name separately
  switch (language) {
    case 'c++': return ProgrammingLanguage.cpp;
    case 'c#': return ProgrammingLanguage.csharp;
    default: return ProgrammingLanguage[language as keyof typeof ProgrammingLanguage];
  }
}

export function getProgrammingLanguageByExtension(extName: string): ProgrammingLanguage | undefined {
  // quality-of-life (also to prevent bugs): Accept extension with or without leading dot
  if (extName.at(0) !== '.') {
    extName = `.${extName}`;
  }
  const lang = extensionMap[extName as keyof typeof extensionMap];
  return lang ? stringToProgrammingLanguage(lang) : undefined;
}

export function isSupportedProgrammingLanguage(extName: string): boolean {
  const lang = getProgrammingLanguageByExtension(extName);
  return lang !== undefined;
}
