import JavaScript from 'tree-sitter-javascript';
import tsPkg from 'tree-sitter-typescript';
import Rust from 'tree-sitter-rust';
import C from 'tree-sitter-c';
import Go from 'tree-sitter-go';
import Java from 'tree-sitter-java';
import Cpp from 'tree-sitter-cpp';
import Kotlin from 'tree-sitter-kotlin';
import PHP from 'tree-sitter-php';
import Python from 'tree-sitter-python';
import Ruby from 'tree-sitter-ruby';
import Swift from 'tree-sitter-swift';
import Csharp from 'tree-sitter-c-sharp';
import logging from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { ProgrammingLanguage, stringToProgrammingLanguage } from '@eave-fyi/eave-stdlib-ts/src/language-mapping.js';

const { typescript: Typescript, tsx } = tsPkg;

// used to typecheck our enum cases as exhuastive
// https://stackoverflow.com/questions/39419170/how-do-i-check-that-a-switch-block-is-exhaustive-in-typescript
function logExhaustiveCaseError(c: never) {
  logging.error(`Unhandled ProgrammingLanguage case: ${c}`);
}

/**
 * Return a tree-sitter grammar corresponding to the programming language
 * `language`.
 * Returns null if there is no grammar found corresponding to `language`, or
 * if the specific `extName` is explicitely unsupported.
 *
 * @param language programming language of source code file.
 * @param extName file extension of the source code file. Expected to contain . prefix (e.g. ".js").
 *                Used for fine-grained grammar selection.
 * @return a tree-sitter grammar (or null)
 */
export function grammarForLanguage(language: string, extName: string): any {
  const pl = stringToProgrammingLanguage(language);
  if (pl === undefined) {
    return null;
  }

  switch (pl) {
    case ProgrammingLanguage.javascript: return JavaScript;
    case ProgrammingLanguage.typescript:
      if (extName === '.tsx') {
        return tsx;
      }
      return Typescript;
    case ProgrammingLanguage.rust: return Rust;
    // case '.h': // TODO: header files won't really have a function body... will be very hard for eave to tell what function does just from signature...
    case ProgrammingLanguage.c: return C;
    case ProgrammingLanguage.go: return Go;
    case ProgrammingLanguage.java: return Java;
    // case '.hh': // TODO: document header file??
    case ProgrammingLanguage.cpp: return Cpp;
    case ProgrammingLanguage.kotlin: return Kotlin;
    case ProgrammingLanguage.php: return PHP;
    // case 'python': return Python; // TODO: we need a special case to handle this in function-parsing.ts, so we'll cut this out for now
    case ProgrammingLanguage.ruby: return Ruby;
    case ProgrammingLanguage.swift: return Swift;
    case ProgrammingLanguage.csharp: return Csharp;
    default:
      logExhaustiveCaseError(pl);
      return null;
  }
}

/**
 * Different tree-sitter language grammars have different names for function nodes.
 * They may also follow different syntax structures, necesitating more or fewer queries.
 *
 * @param language name of programming language to get queries for
 * @return array of queries for gathering all functions and their doc comments for the `language` grammar
 */
export function getFunctionDocumentationQueries(language: string, funcMatcher: string, commentMatcher: string): string[] {
  const pl = stringToProgrammingLanguage(language);
  if (pl === undefined) {
    return [];
  }

  switch (pl) {
    case ProgrammingLanguage.javascript: // js and ts grammar similar enough to share queries
    case ProgrammingLanguage.typescript:
      return [
        // captures root level functions + comments
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,

        // captures comments on functions that are exported on the same line (mostly for JS?)
        // NOTE: this must run after the normal func level query in order to rewrite its bad entries of exported funcs from previous query
        //       w/ the corrected ones containing comment string
        `(
          (comment) @${commentMatcher}* 
          (export_statement declaration:
            (function_declaration) @${funcMatcher}
          )
        )`,

        // captures class level methods
        `(
          (comment) @${commentMatcher}*
          (method_definition) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.rust:
      return [
        // block comment
        `(
          (block_comment) @${commentMatcher}
          (function_item) @${funcMatcher}
        )`,

        // multiple 1-line comments
        `(
          (line_comment) @${commentMatcher}*
          (function_item) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.go:
      return [
        // plain functions
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,

        // struct receiver methods
        `(
          (comment) @${commentMatcher}* 
          (method_declaration) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.cpp: // c/c++ grammar similar enough to share query
    case ProgrammingLanguage.c:
      return [
        `(
          (comment) @${commentMatcher}* 
          (function_definition) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.kotlin:
      return [
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.php:
      return [
        // root level functions
        `(
          (comment) @${commentMatcher}* 
          (function_definition) @${funcMatcher}
        )`,

        // class methods
        `(
          (comment) @${commentMatcher}* 
          (method_declaration) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.ruby:
      return [
        `(
          (comment) @${commentMatcher}* 
          (method) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.swift:
      return [
        // single line doc comments (swift standard)
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,

        // /**/ block comment docs (non-conventional in swift)
        `(
          (multiline_comment) @${commentMatcher}
          (function_declaration) @${funcMatcher}
        )`,
      ];
    case ProgrammingLanguage.java: // java and microsoft java grammar similar enough to share query
    case ProgrammingLanguage.csharp:
      return [
        `(
          (comment) @${commentMatcher}* 
          (method_declaration) @${funcMatcher}
        )`,
      ];
    // case 'python': // TODO: skipped for now for being special snowflake
    default:
      logExhaustiveCaseError(pl);
      return [];
  }
}
