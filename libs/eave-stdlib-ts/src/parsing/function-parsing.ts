import * as crypto from "crypto";
import Parser from "tree-sitter";
import { LogContext, eaveLogger } from "../logging.js";
import { ProgrammingLanguage } from "../programming-langs/language-mapping.js";
import {
  getFunctionDocumentationQueries,
  grammarForFilePathOrName,
} from "./grammars.js";

// document me

// TODO: handling python will require a separate implementation altogether, since this whole algorithm assumes comments come before + outside functions

export type ParsedFunction = {
  // string index where function (or comment, if defined) begins
  start: number;
  // full extracted doc comment preceding function (if any present)
  comment?: string;
  // full extracted function, from signature to end brace (or equivalent)
  func: string;
  // [for external use] updated version of `comment`
  updatedComment?: string;
};

/**
 * Validate that `content` is syntactically valid for the programming language
 * detected from the file extension of `filePath`.
 *
 * @param {Object} params - The parameters for the function.
 * @param {string} params.content - The content of the file to parse.
 * @param {string} params.filePath - The path of the file to parse. The file extension of the source code file is expected to contain . prefix (e.g. ".js"). Used to determine the correct language grammar.
 *
 * @throws {Error} when `content` does not have valid syntax
 */
export function assertValidSyntax({
  content,
  filePath,
}: {
  content: string;
  filePath: string;
}) {
  const parser = new Parser();
  const languageGrammar = grammarForFilePathOrName(filePath);
  if (!languageGrammar) {
    // unable to determine syntactic correctness.
    // This likely means that we couldnt alter `content` either
    return;
  }
  parser.setLanguage(languageGrammar);
  const ptree = parser.parse(content);
  if (ptree.rootNode.hasError()) {
    throw new Error("Syntax error found in file content");
  }
}

/**
 * Parses the content of a file to extract functions and their associated documentation comments.
 *
 * @param {Object} params - The parameters for the function.
 * @param {string} params.content - The content of the file to parse.
 * @param {string} params.filePath - The path of the file to parse. The file extension of the source code file is expected to contain . prefix (e.g. ".js"). Used to determine the correct language grammar.
 * @param {ProgrammingLanguage} params.language - The programming language of the file. Used for constructing grammar queries.
 * @param {LogContext} [params.ctx] - Optional logging context.
 *
 * @returns {ParsedFunction[]} An array of parsed functions, each with associated documentation comments if available.
 *
 * @throws {Error} If no grammar is found for the specified programming language.
 */
export function parseFunctionsAndComments({
  content,
  filePath,
  language,
  ctx = undefined,
}: {
  content: string;
  filePath: string;
  language: ProgrammingLanguage;
  ctx?: LogContext;
}): ParsedFunction[] {
  const parser = new Parser();
  const languageGrammar = grammarForFilePathOrName(filePath);
  if (!languageGrammar) {
    eaveLogger.debug(`No grammar found for ${language}`, ctx);
    return [];
  }
  parser.setLanguage(languageGrammar);
  const ptree = parser.parse(content);

  // map from str hash of func body to ParsedFunction data.
  // func body hash used to prevent duplicate entries of the same exact function
  let fmap: { [key: string]: ParsedFunction } = {};
  const funcMatcher = "_function";
  const commentMatcher = "_doc_comment";

  const queries = getFunctionDocumentationQueries({
    language,
    funcMatcher,
    commentMatcher,
  });

  queries.forEach((queryString) => {
    const query = new Parser.Query(languageGrammar, queryString);
    const newMapEntries = runQuery({
      query,
      rootNode: ptree.rootNode,
      content,
      funcMatcher,
      commentMatcher,
    });
    fmap = {
      ...fmap,
      ...newMapEntries,
    };
  });

  return Object.values(fmap);
}

/**
 * Inserts updated comments into a given content string based on the parsed functions provided.
 * The parsed functions are sorted from high to low to avoid invalidating other indices during insertion.
 * If a function has an updated comment, it is indented and inserted into the content string.
 * If the function has an existing comment, its length is considered to find the beginning of the function signature.
 *
 * @param {string} content - The original content string where comments are to be inserted.
 * @param {ParsedFunction[]} parsedFunctions - An array of parsed functions with their updated comments.
 * @returns {string} The updated content string with the inserted comments.
 */
export function writeUpdatedCommentsIntoFileString(
  content: string,
  parsedFunctions: ParsedFunction[],
): string {
  // sort high to low so we can insert into content string without invalidating other indices
  let newContent = content;
  parsedFunctions
    .sort((a, b) => b.start - a.start)
    .forEach((f) => {
      if (f.updatedComment) {
        indentUpdatedComment(f, content);

        // include comment length (if present) to find beginning of function signature
        // that we must insert the comment before
        let before: number | undefined;
        if (f.comment) {
          before = f.start + f.comment.length;
        }
        newContent = insertDocsComment({
          content: newContent,
          docs: f.updatedComment,
          after: f.start,
          before,
        });
      }
    });

  return newContent;
}

/**
 * Inserts a documentation comment into a given content string at specified positions.
 * Set a value for `params.before` if trying to replace an existing docstring in `params.content`
 * with `params.docs`.
 *
 * @param {Object} params - The parameters for the function.
 * @param {string} params.content - The content string where the documentation comment will be inserted.
 * @param {string} params.docs - The documentation comment to be inserted.
 * @param {number} params.after - The position in the content string after which the documentation comment will be inserted.
 * @param {number} [params.before=params.after] - The position in the content string before which the documentation comment will be inserted. Defaults to the value of `params.after` if not provided.
 * @returns {string} The content string with the inserted documentation comment.
 */
function insertDocsComment({
  content,
  docs,
  after,
  before,
}: {
  content: string;
  docs: string;
  after: number;
  before?: number;
}) {
  if (before === undefined) {
    before = after;
  }

  const precontent = content.slice(0, after);
  const postcontent = content.slice(before);

  // add a newline if one not already present directly following docs
  if (postcontent[0] !== "\n") {
    docs += "\n";
  }

  return `${precontent}${docs}${postcontent}`;
}

/**
 * Executes a given query on a syntax tree and returns a map of parsed functions.
 * The function parses the content of the file, identifies functions and their associated comments,
 * and stores them in a map where the key is a hash of the function content.
 * (Hash key value allows future queries to replace parsed values for a function if
 * multiple queries match the same function; query order matters!)
 *
 * @param {Object} params - The parameters for the function.
 * @param {Parser.Query} params.query - The query to be run on the syntax tree. Expected to have used `funcMatcher` and `commentMatcher` for capture names.
 * @param {Parser.SyntaxNode} params.rootNode - The root node of the syntax tree.
 * @param {string} params.content - The content of the file to be parsed. Used for extracting string content located by `query`.
 * @param {string} params.funcMatcher - The name of the query capture that matches function_declaration (or equivalent) nodes from `rootNode` tree.
 * @param {string} params.commentMatcher - The name of the query capture that matches comment nodes from `rootNode` tree.
 * @returns {Object} A map where the keys are hashes of the function content and the values are objects containing the parsed function data.
 */
function runQuery({
  query,
  rootNode,
  content,
  funcMatcher,
  commentMatcher,
}: {
  query: Parser.Query;
  rootNode: Parser.SyntaxNode;
  content: string;
  funcMatcher: string;
  commentMatcher: string;
}): { [key: string]: ParsedFunction } {
  const fmap: { [key: string]: ParsedFunction } = {};
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
      func: "",
      updatedComment: undefined,
    };

    qmatch.captures.forEach((cap: Parser.QueryCapture) => {
      switch (cap.name) {
        case funcMatcher:
          // track `start` back to closest newline to account for export, or other pre-function-signature gunk
          functionStart = cap.node.startIndex;
          while (functionStart > 0 && content[functionStart - 1] !== "\n") {
            functionStart -= 1;
          }

          functionEnd = cap.node.endIndex;
          minStart = Math.min(functionStart, minStart);
          break;

        case commentMatcher:
          // NOTE: this matcher may be found multiple times per function, due to use of * in query.
          // Check if this matched comment is a continuation (1-line comment on next line)
          // of the previous matched comment. Characters between the end of the prev comment and start of
          // this one should only contain whitespace, but MUST contain exactly one newline.
          if (
            commentEnd === undefined ||
            !content
              .slice(commentEnd, cap.node.startIndex)
              .match(/^[^\S\n]*\n[^\S\n]*$/)
          ) {
            // begin new comment chunk (block or series of 1-line)
            commentStart = cap.node.startIndex;
            minStart = commentStart;
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
    if (
      commentEnd &&
      functionStart &&
      content.slice(commentEnd, functionStart).trim() !== ""
    ) {
      // reset funcData as if comment was not set in it
      funcData.comment = undefined;
      minStart = functionStart;
    }

    // guard against possible empty captures list
    if (functionStart) {
      funcData.func = content.slice(functionStart, functionEnd);
      funcData.start = minStart;
      const funcHash = crypto
        .createHash("md5")
        .update(funcData.func)
        .digest("hex");
      fmap[funcHash] = funcData;
    }
  });
  return fmap;
}

/**
 * Updates the indentation of a parsed function's comment to match the function's indentation level.
 * If the function does not have an updated comment, it will return without making changes.
 * This function only works for languages where doc comments should be at the same
 * indentation level as the function signature they document (i.e. not Python).
 *
 * @param {ParsedFunction} funcData - The parsed function data including its signature, start position, and updated comment.
 * @param {string} content - The original content where the function is located.
 */
function indentUpdatedComment(funcData: ParsedFunction, content: string) {
  if (!funcData.updatedComment) {
    return;
  }

  // extract the indentation level from function signature
  const m = funcData.func.match(/^\s*/);
  const indent = m![0];

  // only add leading indent on first line if indent doesnt already match
  const needsLeadingIndent =
    content.slice(
      Math.max(funcData.start - (indent.length + 1), 0),
      funcData.start,
    ) !== `\n${indent}`;
  funcData.updatedComment = `${
    needsLeadingIndent ? indent : ""
  }${funcData.updatedComment.trim().split("\n").join(`\n${indent}`)}`;
}
