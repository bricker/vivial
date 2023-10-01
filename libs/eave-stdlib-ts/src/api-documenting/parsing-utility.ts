import Parser from "tree-sitter";
import { ProgrammingLanguage, getProgrammingLanguageByFilePathOrName, getProgrammingLanguageByExtension } from "../programming-langs/language-mapping.js";
import { LogContext } from "../logging.js";
import { CtxArg } from "../requests.js";
import assert from "node:assert";
import nodePath from "node:path";
import { grammarForFilePathOrName, grammarForLanguage } from "../parsing/grammars.js";
import { assertPresence, normalizeExtName } from "../util.js";

export class CodeFile {
  path: string;
  contents?: string;

  constructor({path, contents}: { path: string; contents?: string; }) {
    this.path = path;
    this.contents = contents;
  }

  get language(): ProgrammingLanguage | undefined {
    return getProgrammingLanguageByFilePathOrName(this.path);
  }

  get dirname(): string {
    return nodePath.dirname(this.path);
  }

  set dirname(newValue: string) {
    const p = nodePath.parse(this.path);
    p.dir = newValue;

    const newPath = nodePath.format(p);
    this.path = newPath;
  }

  get extname(): string {
    return nodePath.extname(this.path);
  }

  set extname(newValue: string) {
    newValue = normalizeExtName(newValue);
    const p = nodePath.parse(this.path);
    p.base = ""; // node ignores p.ext and p.name if p.base is provided
    p.ext = newValue;

    const newPath = nodePath.format(p);
    this.path = newPath;
  }
}

export class ParsingUtility {
  private readonly ctx: LogContext;

  constructor({ ctx }: CtxArg) {
    this.ctx = ctx;
  }

  parseCode({ file }: { file: CodeFile }): Parser.Tree {
    const parser = this.makeParser({ file });
    assertPresence(file.contents);
    return parser.parse(file.contents);
  }

  makeParser({ file }: { file: CodeFile }): Parser {
    const grammar = grammarForFilePathOrName(file.path);
    const parser = new Parser();
    parser.setLanguage(grammar);
    return parser;
  }

  /**
   * Given a relative file path, returns the full local file path if it exists.
   */
  getLocalFilePath({
    file,
    relativeFilePath,
  }: {
    file: CodeFile;
    relativeFilePath: string;
  }): string {
    relativeFilePath = relativeFilePath.replace(/'|"/g, "");
    // FIXME: Remove specific extension names
    const isSupportedFile = file.extname === ".js" || file.extname === ".ts";

    // Don't use path.isAbsolute() here because we're checking node imports, which likely won't start with a /
    const isLocal = relativeFilePath.at(0) === ".";
    if (!isSupportedFile || !isLocal) {
      return "";
    }

    const fullPath = `${file.path}/../${relativeFilePath}`;
    return nodePath.normalize(fullPath);
  }

  changeFileExtension({ filePathOrName, to }: { filePathOrName: string, to: string }): string {
    const p = nodePath.parse(filePathOrName);
    p.base = ""; // node ignores p.ext and p.name if p.base is provided
    p.ext = normalizeExtName(to);
    return nodePath.format(p);
  }
}