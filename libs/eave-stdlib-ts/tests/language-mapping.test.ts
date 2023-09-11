import anyTest, { TestFn } from 'ava';
import { ProgrammingLanguage, getProgrammingLanguageByExtension, isSupportedProgrammingLanguage, stringToProgrammingLanguage } from '../src/language-mapping.js';
import { TestContextBase, TestUtil } from '../src/test-util.js';

const test = anyTest as TestFn<TestContextBase>;

test.beforeEach((t) => {
  t.context = {
    u: new TestUtil(),
  };
});

test('stringToProgrammingLanguage with valid language name', (t) => {
  t.is(stringToProgrammingLanguage('typescript'), ProgrammingLanguage.typescript);
});

test('stringToProgrammingLanguage with valid language name uppercase', (t) => {
  t.is(stringToProgrammingLanguage('TYPESCRIPT'), ProgrammingLanguage.typescript);
});

test('stringToProgrammingLanguage with special names', (t) => {
  t.is(stringToProgrammingLanguage('c++'), ProgrammingLanguage.cpp);
  t.is(stringToProgrammingLanguage('c#'), ProgrammingLanguage.csharp);
});

test('stringToProgrammingLanguage with invalid language name', (t) => {
  t.is(stringToProgrammingLanguage(t.context.u.anystr()), undefined);
});

test('getProgrammingLangaugeByExtension with valid extension with leading dot', async (t) => {
  const v = getProgrammingLanguageByExtension('.ts');
  t.is(v, ProgrammingLanguage.typescript);
});

test('getProgrammingLangaugeByExtension with valid extension without leading dot', async (t) => {
  const v = getProgrammingLanguageByExtension('ts');
  t.is(v, ProgrammingLanguage.typescript);
});

test('getProgrammingLangaugeByExtension with invalid extension', async (t) => {
  const v = getProgrammingLanguageByExtension(t.context.u.anystr());
  t.is(v, undefined);
});

test('getProgrammingLangaugeByExtension with unsupported extension', async (t) => {
  const v = getProgrammingLanguageByExtension('.f90');
  t.is(v, undefined);
});

test('isSupportedProgrammingLanguage with supported extension', async (t) => {
  const v = isSupportedProgrammingLanguage('.ts');
  t.true(v);
});

test('isSupportedProgrammingLanguage with unsupported extension', async (t) => {
  const v = isSupportedProgrammingLanguage('.f90');
  t.false(v);
});
