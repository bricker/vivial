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

test('javascript grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.js';
  const langauge = 'javascript';
  const content = `const appConfig = require('./src/config.js');

function foo() {
  console.log('foo');
}

class MyClass {
  bar() {
    return "bar";
  }
}

module.exports = function baz() {
  return "baz";
}

/**
 * Doc comment
 * @param to be replaced
 * @returns by parse code
 */
async function fizzbuzz() {
  return 'fizzbuzz';
}
`;

  // WHEN content parsed by tree-sitter grammars
  const funcDocsArray = parseFunctionsAndComments(content, extname, langauge);

  // THEN all functions should be detected/parsed by queries
  // TODO: 3 instead of 4 bcus cjs module export function on same line is not detected by current
  // queries and is probably better that way? Without some custom logic to see if assignment
  // is to module.exports, we would end up generating docs for lambda functions etc as well,
  // which we probably don't want.
  t.deepEqual(funcDocsArray.length, 3);

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
  const expectedUpdatedContent = `const appConfig = require('./src/config.js');

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
  bar() {
    return "bar";
  }
}

module.exports = function baz() {
  return "baz";
}

/**
 * Great new docs
 * @param Eave wrote
 * @return very well
 */
async function fizzbuzz() {
  return 'fizzbuzz';
}
`;
  t.deepEqual(updatedContent, expectedUpdatedContent);
});

test('rust grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.rs';
  const langauge = 'rust';
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

test('C grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.c';
  const langauge = 'c';
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

test('C++ grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.cpp';
  const langauge = 'c++';
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

test('Go grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.go';
  const langauge = 'go';
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

test('Java grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.java';
  const langauge = 'java';
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

test('Kotlin grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.kt';
  const langauge = 'kotlin';
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

test('PHP grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.php';
  const langauge = 'php';
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

test('Ruby grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.rb';
  const langauge = 'ruby';
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

test('Swift grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.swift';
  const langauge = 'swift';
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

test('C# grammar queries adds/replaces all doc comments correctly', (t) => {
  // GIVEN string content of a file (and langauge/ext data)
  // (note: function variable string indentation is important; dont adjust to match this file's indentation level)
  const extname = '.cs';
  const langauge = 'c#';
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