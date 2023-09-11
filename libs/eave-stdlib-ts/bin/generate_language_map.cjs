const fs = require('fs').promises;
// eslint-disable-next-line import/no-extraneous-dependencies
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

      // TODO: this is a bad assumption. Typescript (and others) gets overwritten my XML :(
      transformedFileObject[ext] = langName;
    }
  });

  // ensure common file types have correct mapping
  transformedFileObject['.tsx'] = 'TypeScript';
  transformedFileObject['.ts'] = 'TypeScript';
  transformedFileObject['.ex'] = 'Elixir';
  transformedFileObject['.rs'] = 'Rust';
  transformedFileObject['.r'] = 'R';
  transformedFileObject['.cs'] = 'C#';

  // write to local file as json for easier access by prod TS code
  const jsonString = JSON.stringify(transformedFileObject, null, 2);
  await fs.writeFile(`${process.env['EAVE_HOME']}/libs/eave-stdlib-ts/src/languages.json`, jsonString, 'utf8');
}

main();
