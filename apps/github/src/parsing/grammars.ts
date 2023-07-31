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
    case '.py': return Python;
    case '.rb': return Ruby;
    case '.swift': return Swift;
    case '.cs': return Csharp;
    default: return null;
  }
}
