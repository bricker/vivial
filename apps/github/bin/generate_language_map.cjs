const fs = require('fs').promises;
const yaml = require('js-yaml');

async function main() {
  // download latest lang file from https://github.com/github-linguist
  const fileResp = await fetch('https://raw.githubusercontent.com/github-linguist/linguist/master/lib/linguist/languages.yml');
  const fileString = await fileResp.text();

  // ingest file content
  const fileObject = yaml.load(fileString);

  // transform into extension -> lang name map
  const transformedFileObject = {};
  Object.keys(fileObject).forEach((langName) => {
    if (!fileObject[langName]?.extensions) { return; }

    for (const ext of fileObject[langName].extensions) {
      // it is possible that some langauges will share some extensions (e.g. C/C++)
      // but for simplicity I'll assume if that happens, they're similar enough not
      // to matter much if we correlate the ext with only one of the languages
      transformedFileObject[ext] = langName;
    }
  });

  // write to local file as json for easier access by prod TS code
  const jsonString = JSON.stringify(transformedFileObject);
  await fs.writeFile('../languages.json', jsonString, 'utf8');
}

main();
