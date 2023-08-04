import test from 'ava';
import { parseFunctionsAndComments, writeDocsIntoFileString } from '../../src/parsing/function-parsing.js';

test('typescript grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.ts';
  const langauge = 'typescript';
  const content = `import { appConfig } from './src/config.js';

function foo() {
  console.log('foo');
}

class MyClass {
  bar(): string {
    return "bar";
  }
}

export function baz(): string {
  return "baz";
}

/**
 * Doc comment
 * @param to be replaced
 * @returns by parse code
 */
async function fizzbuzz(): Promise<string> {
  return 'fizzbuzz';
}
`;

  // WHEN content parsed by tree-sitter grammars
  const funcDocsArray = parseFunctionsAndComments(content, extname, langauge);

  // THEN all functions should be detected/parsed by queries
  t.deepEqual(funcDocsArray.length, 4);

  // WHEN new doc comments are written into file content
  for (let i = 0; i < funcDocsArray.length; i += 1) {
    funcDocsArray[i]!.updatedComment = `/**
 * Great new docs
 * @param Eave wrote
 * @return very well
 */`;
  }
  const updatedContent = writeDocsIntoFileString(content, funcDocsArray);

  // THEN updated file content should be fully documented at correct indentation levels
  const expectedUpdatedContent = `import { appConfig } from './src/config.js';

/**
 * Great new docs
 * @param Eave wrote
 * @return very well
 */
function foo() {
  console.log('foo');
}

class MyClass {
  /**
   * Great new docs
   * @param Eave wrote
   * @return very well
   */
  bar(): string {
    return "bar";
  }
}

/**
 * Great new docs
 * @param Eave wrote
 * @return very well
 */
export function baz(): string {
  return "baz";
}

/**
 * Great new docs
 * @param Eave wrote
 * @return very well
 */
async function fizzbuzz(): Promise<string> {
  return 'fizzbuzz';
}
`;
  t.deepEqual(updatedContent, expectedUpdatedContent);
});
