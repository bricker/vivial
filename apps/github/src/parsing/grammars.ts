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

const { typescript, tsx } = tsPkg;

/**
 * Return a tree-sitter grammar corresponding to the programming language
 * of a file with the extension `extName`.
 * Returns null if there is no grammar found corresponding to `extName`.
 *
 * @param extName file extension of the source code file. Expected to contain . prefix (e.g. ".js").
 *                Used to determine file language.
 * @return a tree-sitter grammar (or null)
 */
export function grammarFromExtension(extName: string): any {
  switch (extName) {
    case '.js': return JavaScript;
    case '.ts': return typescript;
    case '.tsx': return tsx;
    case '.rs': return Rust;
    case '.h': // TODO: header files won't really have a function body... will be very hard for eave to tell what function does just from signature...
    case '.c': return C;
    case '.go': return Go;
    case '.java': return Java;
    case '.hh': // TODO: document header file??
    case '.cc':
    case '.c++':
    case '.cxx':
    case '.cpp': return Cpp;
    case '.kt': return Kotlin;
    case '.php': return PHP;
    // case '.py': return Python; // TODO: we need a special case to handle this in function-parsing.ts, so we'll cut this out for now
    case '.rb': return Ruby;
    case '.swift': return Swift;
    case '.cs': return Csharp;
    default: return null;
  }
}

// TODO: write tests for this one; make sure these queries actually work
/**
 * Different tree-sitter language grammars have different names for function nodes.
 * They may also follow different syntax structures, necesitating more or fewer queries.
 *
 * @param language name of programming language to get queries for
 * @return array of queries for gathering all functions and their doc comments for the `language` grammar
 */
export function getFunctionDocumentationQueries(language: string, funcMatcher: string, commentMatcher: string): string[] {
  switch (language.toLowerCase()) {
    case 'javascript': // js and ts grammar similar enough to share queries
    case 'typescript':
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
    case 'rust':
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
    case 'go':
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
    case 'c++': // c/c++ grammar similar enough to share query
    case 'c':
      return [
        `(
          (comment) @${commentMatcher}* 
          (function_definition) @${funcMatcher}
        )`,
      ];
    case 'kotlin':
      // TODO: kotlin grammar may be out of date. It doesnt seem to parse class extensions correctly
      return [
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,
      ];
    case 'php':
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
    case 'ruby':
      return [
        `(
          (comment) @${commentMatcher}* 
          (method) @${funcMatcher}
        )`,
      ];
    case 'swift':
      return [ // comment only covers single line. would need (multiline_comment) to capture /* */ comments
        `(
          (comment) @${commentMatcher}* 
          (function_declaration) @${funcMatcher}
        )`,
      ];
    case 'java': // java and microsoft java grammar similar enough to share query
    case 'c#':
      return [
        `(
          (comment) @${commentMatcher}* 
          (method_declaration) @${funcMatcher}
        )`,
      ];
    // case 'python': // TODO: skipped for now for being special snowflake
    default:
      return [];
  }
}
