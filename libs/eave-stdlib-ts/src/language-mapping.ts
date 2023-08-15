import fs from 'fs';

let extensionMap: { [key: string]: string } | undefined;

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
