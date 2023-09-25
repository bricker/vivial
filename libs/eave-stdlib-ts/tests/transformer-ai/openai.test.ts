import test from "ava";
import { formatprompt } from "../../src/transformer-ai/openai.js";

test("formatprompt should remove common leading indentation from multiline strings", (t) => {
  const input = `
    Hello,
      This is a test.
        Indentation matters.
    `;
  const expectedOutput = `
Hello,
  This is a test.
    Indentation matters.
`;
  const result = formatprompt(input);
  t.is(result, expectedOutput);
});

test("formatprompt should handle multiple multiline strings", (t) => {
  const input1 = `
    Standard indentation.
    Oh look, some code!`;
  const input2 = `function wow() {
  console.log('separate indent level')
}`;
  const input3 = `
            now even bigger
            indentation levels.
            `;
  const expectedOutput = `
Standard indentation.
Oh look, some code!
function wow() {
  console.log('separate indent level')
}

now even bigger
indentation levels.
`;
  const result = formatprompt(input1, input2, input3);
  t.is(result, expectedOutput);
});

test("formatprompt should not modify single-line strings", (t) => {
  const input = "This is a single-line string";
  const result = formatprompt(input);
  t.is(result, input);
});

test("formatprompt should handle empty strings", (t) => {
  const input = "";
  const result = formatprompt(input);
  t.is(result, input);
});

test("formatprompt should handle strings with only whitespace", (t) => {
  const input = "    \t  \n   \t  \n  \t \n";
  const result = formatprompt(input);
  t.is(result, input);
});

test("formatprompt should ignore separating lines with only whitespace", (t) => {
  const input = `
    Line 1
    line after this one has TONS of whitespace
              
    and the one after this one has none!

    this text should all be made flat.
    `;
  const expectedOutput = `
Line 1
line after this one has TONS of whitespace
          
and the one after this one has none!

this text should all be made flat.
`;
  const result = formatprompt(input);
  t.is(result, expectedOutput);
});
