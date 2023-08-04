import Parser from 'tree-sitter';
import * as crypto from 'crypto';
import { getFunctionDocumentationQueries, grammarFromExtension } from './grammars.js';

/*
TODO 
handling python will require a separate implementation altogether

detects multiple single-line comments in a row as separate comments. no differenctiation whether separated by newlines or not.
  this affects langs like swift+go where docs are typically in multiple single line comments
  will require manual parsing of comment nodes to see if start/end idx all line up or not and stitching strings together
*/

export type ParsedFunction = {
  // string index where function (or comment, if defined) begins
  start: number
  // full extracted doc comment preceding function (if any present)
  comment: string | undefined
  // full extracted function, from signature to end brace (or equivalent)
  func: string
  // [for external use] updated version of `comment`
  updatedComment: string | undefined
}

/**
 * Use tree-sitter to extract functions and their doc comments from
 * the provided file `content`.
 *
 * @param content string content of a source code file
 * @param extName file extension of the source code file. Expected to contain . prefix (e.g. ".js").
 *                Used to determine the correct language grammar.
 * @param language programming language of `content`. Used for constructing grammar queries.
 * @returns array of function data parsed from `content`
 */
export function parseFunctionsAndComments(content: string, extName: string, language: string): ParsedFunction[] {
  const parser = new Parser();
  const languageGrammar = grammarFromExtension(extName);
  parser.setLanguage(languageGrammar);
  const ptree = parser.parse(content);

  // map from str hash of func body to ParsedFunction data.
  // func body hash used to prevent duplicate entries of the same exact function
  const fmap: { [key: string]: ParsedFunction } = {};
  const funcMatcher = '_function';
  const commentMatcher = '_doc_comment';

  const queries = getFunctionDocumentationQueries(language, funcMatcher, commentMatcher);

  queries.forEach((queryString) => {
    const query = new Parser.Query(languageGrammar, queryString);
    runQuery(query, ptree.rootNode, content, fmap, funcMatcher, commentMatcher);
  });

  return Object.values(fmap);
}

/**
 * Writes new doc comments into `content`, returning the updated file content string.
 *
 * @param content file string to write `fmap` comments into
 * @param parsedFunctions array of functions+comments data from `content`
 * @returns updated file content string
 */
export function writeDocsIntoFileString(content: string, parsedFunctions: ParsedFunction[]): string {
  // sort high to low so we can insert into content string without invalidating other indices
  let newContent = content;
  parsedFunctions.sort((a, b) => b.start - a.start).forEach((f) => {
    if (f.updatedComment) {
      const newDocs = indentDocs(f.func, f.updatedComment);

      // include comment length (if present) to find beginning of function signature
      // that we must insert the comment before
      let before: number | undefined;
      if (f.comment) {
        before = f.start + f.comment.length;
      }
      newContent = insertDocs(newContent, newDocs, f.start, before);
    }
  });

  return newContent;
}

/**
 * Inserts docs between `after` and `before`.
 * Set a value for `before` if trying to replace an existing docstring in `content`
 * with `docs`.
 *
 * @param content string to have docs inserted into
 * @param docs string to insert into content
 * @param after index in content to put docs after
 * @param before index in content to put docs before. (set to after if undefined)
 * @returns content with `docs` inserted
 */
function insertDocs(content: string, docs: string, after: number, before?: number) {
  if (before === undefined) {
    before = after;
  }

  const precontent = content.slice(0, after);
  const postcontent = content.slice(before);

  // add a newline if one not already present directly following docs
  let i = 0;
  let needsNewline = true;
  while (i < postcontent.length && /\s/.test(postcontent[i]!)) {
    if (postcontent[i] === '\n') {
      needsNewline = false;
      break;
    }
    i += 1;
  }
  if (needsNewline) {
    docs += '\n';
  }

  return `${precontent}${docs}${postcontent}`;
}

/**
 * Runs `query` on `content`, creating ParsedFunction objects to add to `fmap`.
 * Mutates `fmap` in-place, rather than returning results.
 *
 * @param query match query to run on `content`. Expected to have used `funcMatcher` and `commentMatcher` for capture names.
 * @param rootNode parse tree node
 * @param content file content used to create `rootNode`. Used for extracting string content located by `query`
 * @param fmap map object to store `query` results in
 * @param funcMatcher name used by `query` to capture function_declaration (or equivilant) nodes from `rootNode` tree
 * @param commentMatcher name used by `query` to capture comment nodes from `rootNode` tree
 */
function runQuery(
  query: Parser.Query,
  rootNode: Parser.SyntaxNode,
  content: string,
  fmap: { [key: string]: ParsedFunction },
  funcMatcher: string,
  commentMatcher: string,
): void {
  const matches = query.matches(rootNode);

  matches?.forEach((qmatch) => {
    let start;
    let end;
    let commentEnd;
    let minStart = Infinity;
    // stuffed w/ placeholder values that will always be overwritten
    const funcData: ParsedFunction = {
      start: Infinity,
      comment: undefined,
      func: '',
      updatedComment: undefined,
    };

    qmatch.captures.forEach((cap) => {
      switch (cap.name) {
        case funcMatcher:
          // track `start` back to closest newline to account for export, or other pre-function-signature gunk
          start = cap.node.startIndex;
          while (start > 1 && content[start - 1] !== '\n') {
            start -= 1;
          }

          end = cap.node.endIndex;
          minStart = Math.min(start, minStart);
          break;

        case commentMatcher:
          commentEnd = cap.node.endIndex;
          funcData.comment = content.slice(cap.node.startIndex, cap.node.endIndex);
          // No need to min since we know doc comment will come before func name start (due to query structure).
          // Also prevents the comment star match from pulling in any previous comments
          // (those are currently un-accounted for when extracting docs, only closest comment currently)
          minStart = cap.node.startIndex;
          break;

        default:
          break;
      }
    });

    /*
    Tree-sitter builds a tree (shocking revelation) to represent the parsed syntax of the file.
    S-expressions (basically anything) in the same scope (e.g. contained w/in class, or file root level)
    are sibling nodes in the CST that tree-sitter constructs.

    A query like the following groups a sequence of sibling nodes, which is as close as we can get to
    "next to each other" from a raw tree-sitter query
    https://tree-sitter.github.io/tree-sitter/using-parsers#the-query-api
    (
      (comment)*
      (function_declaration)
    )
    This query matches any combination of sibling nodes that satisfy that order.
    For example, if that query were executed on the following file (line numbers for reference):
    ```
    1 // some comment
    2 function someRootLevelFunction() { ... }
    3 function otherRootLevelFunction() { ... }
    ```
    The query would find the following matching pairs of syntax nodes (referencing line numbers for brevity):
    [(1,2), (1,3)]

    This isn't desirable since we are actually looking for neighbors, not just any siblings.
    This behavior is occasionally masked by the closest sibling nodes being valid neighbors.

    To account for this, we are manually ensuring the characters between comment end and function
    beginning contain only white-space, or else we don't consider the comment and function a
    valid pairing. (This assumption may also be rife with its own issues. TBD)
    */
    // ensure comment-function pairing are really next to each other (not just sibling nodes)
    if (commentEnd && start && content.slice(commentEnd, start).trim() !== '') {
      // reset funcData as if comment was not set in it
      funcData.comment = undefined;
      minStart = start;
    }

    // guard against possible empty captures list
    if (start) {
      funcData.func = content.slice(start, end);
      funcData.start = minStart;
      const funcHash = crypto.createHash('md5').update(funcData.func).digest('hex');
      fmap[funcHash] = funcData;
    }
  });
}

/**
 * Adds indentation (matching the level of `funcString`) to docs.
 * `funcString` must not be trimmed; expected to have indentation leading whitespace.
 * This function only works for languages where doc comments should be at the same
 * indentation level as the function signature they document (i.e. not Python)
 *
 * @param funcString string to copy indentation level from
 * @param docs string to add indentation to
 * @returns Indented `docs` string
 */
function indentDocs(funcString: string, docs: string) {
  // extract a matching indentation level from function signature
  let i = 0;
  while (i < funcString.length && /\s/.test(funcString[i]!)) {
    i += 1;
  }
  const indent = funcString.slice(0, i);
  return `${indent}${docs.trim().split('\n').join(`\n${indent}`)}`;
}
