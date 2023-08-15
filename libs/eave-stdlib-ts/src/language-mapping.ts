import fs from 'fs';

let extensionMap: { [key: string]: string } | undefined;

export enum ProgrammingLanguage {
  javascript,
  typescript,
  rust,
  c,
  go,
  java,
  kotlin,
  ruby,
  cpp,
  php,
  swift,
  csharp,
}

/**
 * Converts string to enum case. Necessary to translate "c++" to cpp enum case.
 * @param lang string to convert, if possible
 * @return ProgrammingLanguage enum case, or undefined if `lang` is not a case
 */
export function stringToProgrammingLanguage(lang: string): ProgrammingLanguage | undefined {
  const language = lang.toLowerCase();
  if (language === 'c++') {
    return ProgrammingLanguage.cpp;
  }
  return ProgrammingLanguage[language as keyof typeof ProgrammingLanguage];
}

export async function isSupportedProgrammingLanguage(extName: string): Promise<boolean> {
  if (!extensionMap) {
    await loadExtensionMap();
  }
  return stringToProgrammingLanguage(extensionMap![extName] || '') !== undefined;
}

export async function loadExtensionMap() {
  const extensionMapString = await fs.promises.readFile('./languages.json', { encoding: 'utf8' });
  extensionMap = JSON.parse(extensionMapString);
}

export async function getExtensionMap(): Promise<{ [key: string]: string }> {
  if (!extensionMap) {
    await loadExtensionMap();
    return extensionMap!;
  }
  return extensionMap;
}
