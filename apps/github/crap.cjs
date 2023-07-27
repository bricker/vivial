const Parser = require("tree-sitter");
const typescript = require('tree-sitter-typescript').typescript;
const fs = require('fs').promises;
const crypto = require('crypto');

/*
TODO:
prevent docs write from writing between func name and declaration keywords (if no comment, seek back to nearest \n)
match indentation
sibling nodes...

refactor queries into shared function

--
research on some dumb shit like python doc comments 

detects multiple single-line comments in a row as separate comments. no differenctiation whether separated by newlines or not. 
  How will this affect langs like swift where docs are typically in multiple single line comments? 
  will require manual parsing of comment nodes to see if start/end idx all line up or not and stitching strings together
*/


async function main() {
  const parser = new Parser();
  parser.setLanguage(typescript);

  const content = await fs.readFile('./shit.ts', {encoding: 'utf8'});

  const ptree = parser.parse(content);

  // console.log(ptree.rootNode.toString());
  // return;

  // map from str hash of func body to objs w/ fucn and comment string data
  /* 
  {
    start: int, // index of start in content string (min func.start comment.start)
    comment: string?,
    func: string,
  }
  */
  let fmap = {};
  const funcMatcher = '_function';
  const commentMatcher = '_doc_comment';

  // gather root level functions + comments

  const rootFuncQ = new Parser.Query(typescript, `(
    (comment) @${commentMatcher}* 
    (function_declaration) @${funcMatcher}
  )`);
  runQuery(rootFuncQ, ptree.rootNode, content, fmap, funcMatcher, commentMatcher);


  // capture comments on functions that are exported (mostly for JS?)
  // NOTE: this must run after the normal func level query in order to rewrite its bad entries of exported funcs from previous query
  //       w/ the corrected ones containing comment string
  const exportFuncQ = new Parser.Query(typescript, `(
    (comment) @${commentMatcher}* 
    (export_statement declaration:
      (function_declaration) @${funcMatcher}
    )
  )`);
  runQuery(exportFuncQ, ptree.rootNode, content, fmap, funcMatcher, commentMatcher);

  // gather class level methods

  const classMethodsQ = new Parser.Query(typescript, `(class_declaration
    body: (class_body
      (comment) @${commentMatcher}*
      (method_definition) @${funcMatcher}
    )
  )`);
  runQuery(classMethodsQ, ptree.rootNode, content, fmap, funcMatcher, commentMatcher);

  console.log(`${Object.keys(fmap).length} entires:`)

  // run "update docs on them"

  // sort high to low so we can edit content string without invalidating other indices
  let newContent = content;
  Object.keys(fmap).sort((a,b) => fmap[b].start - fmap[a].start).forEach(key => {
    const f = fmap[key];
//     console.log(`{
//   start: ${f.start},
//   comment: \n"${f.comment}",
//   func: \n"${f.func}"
// }\n`)

    const newDocs = updateDocs(f.func, f.comment);
    let before = undefined;
    if (f.comment) {
      before = f.start + f.comment.length;
    }
    newContent = insertDocs(newContent, newDocs, f.start, before);
  })

  await fs.writeFile('./shit-copy.ts', newContent, { encoding: 'utf8' });
}

/**
 * Inserts docs between `after` and `before`.
 * Set a value for `before` if trying to replace an existing docstring in `content`
 * with `docs`.
 *
 * @param content string to have docs inserted into
 * @param docs string to insert into content
 * @param after int put docs after this index in content
 * @param before int? put docs before this index in content. (set to after if undefined)
 * @returns content with `docs` inserted
 */
function insertDocs(content, docs, after, before = undefined) {
  if (before === undefined) {
    before = after;
  }

  const precontent = content.slice(0, after);
  const postcontent = content.slice(before);

  // add a newline if one not already present directly following docs
  let i = 0;
  let needsNewline = true;
  while (i < postcontent.length && /\s/.test(postcontent[i])) {
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
 * Updates fmap in-place
 *
 * @param {*} query 
 * @param {*} content 
 * @param {*} fmap 
 * @param {*} funcMatcher 
 * @param {*} commentMatcher 
 */
function runQuery(query, rootNode, content, fmap, funcMatcher, commentMatcher) {
  const matches = query.matches(rootNode);
  if (matches) {
    matches.forEach(qmatch => {
      let start, end, minStart, commentEnd;
      minStart = Infinity;
      const funcData = {};

      qmatch.captures.forEach(cap => {
        // console.log(cap.name);
        if (cap.name === funcMatcher) {
          // console.log(`from ix ${cap.node.startIndex}`)
          // track `start` back to closest newline to account for export, or other pre-signature gunk
          start = cap.node.startIndex;
          while (start > 1 && content[start - 1] !== '\n') {
            start -= 1;
          }

          end = cap.node.endIndex;
          minStart = Math.min(start, minStart)
        }
        if (cap.name === commentMatcher) {
          const comment = content.slice(cap.node.startIndex, cap.node.endIndex)
          commentEnd = cap.node.endIndex;
          // console.log(`doc string: ${comment}`)
          funcData.comment = comment
          // no need to min since we know doc comment will come before func name start (due to query structure)
          // Also prevents the comment star match from pulling in any previous comments (those are currently un-accounted for when extracting docs, only closest comment currently)
          minStart = cap.node.startIndex // Math.min(minStart, cap.node.startIndex)
        }
      })

      /*
      Tree-sitter builds a tree (shocking) to represent the parsed syntax of the file.
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
      // console.log(`between: ${content.slice(commentEnd, start)}`);
      if (commentEnd && start && content.slice(commentEnd, start).trim() !== '') {
        // reset funcData as if comment was not applied to it
        // console.log(`unsetting ${funcData.comment} from ${start}`)
        funcData.comment = undefined;
        minStart = start;
      }

      // guard against empty captures list
      if (start) {
        funcData.func = content.slice(start, end);
        funcData.start = minStart;
        fmap[hash(funcData.func)] = funcData;
        // console.log(`adding to map: ${funcData.func}`)
      }
    })
  }
}

// dummy stub
function updateDocs(funcString, currDocs = undefined) {
  if (currDocs) {
    return currDocs;
  }
  // trim?
  let docs = `/**
 * Very real docstring
 * such documented, veryu wow
 * @returns somethign
 */`;

  // console.log(funcString);
  // extract indentation from first line of function
  let i = 0;
  while (i < funcString.length && /\s/.test(funcString[i])) {
    i += 1;
  }
  const indent = funcString.slice(0, i);
  docs = `${indent}${docs.split('\n').join(`\n${indent}`)}`;

  return docs;
}

// helper
function hash(s) {
  return crypto.createHash('md5').update(s).digest('hex');
}

main();
