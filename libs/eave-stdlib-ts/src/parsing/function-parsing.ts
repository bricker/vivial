import Parser from 'tree-sitter';
import * as crypto from 'crypto';
import { getFunctionDocumentationQueries, grammarForLanguage } from './grammars.js';
import logging, { LogContext } from '../logging.js';

// TODO: handling python will require a separate implementation altogether, since this whole algorithm assumes comments come before + outside functions

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
export function parseFunctionsAndComments({
  content,
  extName,
  language,
  ctx = undefined,
}: {
  content: string,
  extName: string,
  language: string,
  ctx?: LogContext,
}): ParsedFunction[] {
  const parser = new Parser();
  const languageGrammar = grammarForLanguage({ language, extName });
  if (!languageGrammar) {
    logging.debug(`No grammar found for ${language}`, ctx);
    return [];
  }
  parser.setLanguage(languageGrammar);
  const ptree = parser.parse(content);

  // map from str hash of func body to ParsedFunction data.
  // func body hash used to prevent duplicate entries of the same exact function
  const fmap: { [key: string]: ParsedFunction } = {};
  const funcMatcher = '_function';
  const commentMatcher = '_doc_comment';

  const queries = getFunctionDocumentationQueries({ language, funcMatcher, commentMatcher });

  queries.forEach((queryString) => {
    const query = new Parser.Query(languageGrammar, queryString);
    runQuery({ query, rootNode: ptree.rootNode, content, fmap, funcMatcher, commentMatcher });
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
export function writeUpdatedCommentsIntoFileString(content: string, parsedFunctions: ParsedFunction[]): string {
  // sort high to low so we can insert into content string without invalidating other indices
  let newContent = content;
  parsedFunctions.sort((a, b) => b.start - a.start).forEach((f) => {
    if (f.updatedComment) {
      indentUpdatedComment(f, content);

      // include comment length (if present) to find beginning of function signature
      // that we must insert the comment before
      let before: number | undefined;
      if (f.comment) {
        before = f.start + f.comment.length;
      }
      newContent = insertDocsComment({ content: newContent, docs: f.updatedComment, after: f.start, before });
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
function insertDocsComment({
  content,
  docs,
  after,
  before,
}: {
  content: string,
  docs: string,
  after: number,
  before?: number,
}) {
  if (before === undefined) {
    before = after;
  }

  const precontent = content.slice(0, after);
  const postcontent = content.slice(before);

  // add a newline if one not already present directly following docs
  if (postcontent[0] !== '\n') {
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
function runQuery({
  query,
  rootNode,
  content,
  fmap,
  funcMatcher,
  commentMatcher,
}: {
  query: Parser.Query,
  rootNode: Parser.SyntaxNode,
  content: string,
  fmap: { [key: string]: ParsedFunction },
  funcMatcher: string,
  commentMatcher: string,
}): void {
  const matches = query.matches(rootNode);

  matches?.forEach((qmatch: Parser.QueryMatch) => {
    let functionStart;
    let functionEnd;
    let commentStart: number | undefined;
    let commentEnd: number | undefined;
    let minStart = Infinity;
    // stuffed w/ placeholder values that will always be overwritten
    const funcData: ParsedFunction = {
      start: Infinity,
      comment: undefined,
      func: '',
      updatedComment: undefined,
    };

    qmatch.captures.forEach((cap: Parser.QueryCapture) => {
      switch (cap.name) {
        case funcMatcher:
          // track `start` back to closest newline to account for export, or other pre-function-signature gunk
          functionStart = cap.node.startIndex;
          while (functionStart > 0 && content[functionStart - 1] !== '\n') {
            functionStart -= 1;
          }

          functionEnd = cap.node.endIndex;
          minStart = Math.min(functionStart, minStart);
          break;

        case commentMatcher:
          // NOTE: this matcher may be found multiple times per function, due to use of * in query.
          // Check if this matched comment is a continuation (1-line comment on next line)
          // of the previous matched comment. Characters between the end of the prev comment and start of
          // this one should only contain whitespace, but MUST contain a newline.
          if (commentEnd === undefined || !content.slice(commentEnd, cap.node.startIndex).match(/\s*\n\s*/)) {
            // begin new comment chunk (block or series of 1-line)
            commentStart = cap.node.startIndex;
            minStart = Math.min(commentStart, minStart);
          }
          commentEnd = cap.node.endIndex;
          break;

        default:
          break;
      }
    });

    if (commentStart && commentEnd) {
      funcData.comment = content.slice(commentStart, commentEnd);
    }

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
    // ensure comment-function pairing are really next to each other (not just sibling nodes).
    // There should be nothing between the end of the doc comment and the function signature.
    if (commentEnd && functionStart && content.slice(commentEnd, functionStart).trim() !== '') {
      // reset funcData as if comment was not set in it
      funcData.comment = undefined;
      minStart = functionStart;
    }

    // guard against possible empty captures list
    if (functionStart) {
      funcData.func = content.slice(functionStart, functionEnd);
      funcData.start = minStart;
      const funcHash = crypto.createHash('md5').update(funcData.func).digest('hex');
      fmap[funcHash] = funcData;
    }
  });
}

/**
 * Adds indentation (matching the level of `funcData.func`) to `funcData.updatedComment`.
 * Updates `funcData` in-place rather than returning a value.
 * This function only works for languages where doc comments should be at the same
 * indentation level as the function signature they document (i.e. not Python).
 *
 * @param funcData function and comment + meta data
 * @param content file content function + comment is contained in. Used for indent calculations
 */
function indentUpdatedComment(funcData: ParsedFunction, content: string) {
  if (!funcData.updatedComment) {
    return;
  }

  // extract the indentation level from function signature
  let i = 0;
  while (i < funcData.func.length && /\s/.test(funcData.func[i]!)) {
    i += 1;
  }
  const indent = funcData.func.slice(0, i);

  // only add leading indent on first line if indent doesnt already match
  const needsLeadingIndent = content.slice(Math.max(funcData.start - (indent.length + 1), 0), funcData.start) !== `\n${indent}`;
  funcData.updatedComment = `${needsLeadingIndent ? indent : ''}${funcData.updatedComment.trim().split('\n').join(`\n${indent}`)}`;
}
