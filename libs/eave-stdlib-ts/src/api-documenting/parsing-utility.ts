import nodePath from "node:path";
import Parser from "tree-sitter";
import { grammarForFilePathOrName } from "../parsing/grammars.js";
import {
  ProgrammingLanguage,
  getProgrammingLanguageByFilePathOrName,
} from "../programming-langs/language-mapping.js";
import { JsonObject } from "../types.js";
import { normalizeExtName } from "../util.js";

export class CodeFile {
  contents: string;
  path: string;
  private __memo_tree__?: Parser.Tree;

  constructor({ path, contents }: { path: string; contents: string }) {
    this.path = path;
    this.contents = contents;
  }

  get asJSON(): JsonObject {
    return {
      path: this.path,
      language: this.language,
    };
  }

  get tree(): Parser.Tree {
    if (this.__memo_tree__ !== undefined) {
      return this.__memo_tree__;
    }

    const tree = parseCode({ filePathOrName: this.path, code: this.contents });
    this.__memo_tree__ = tree;
    return this.__memo_tree__;
  }

  get language(): ProgrammingLanguage | undefined {
    return getProgrammingLanguageByFilePathOrName(this.path);
  }

  get dirname(): string {
    return nodePath.dirname(this.path);
  }

  // set dirname(newValue: string) {
  //   const p = nodePath.parse(this.path);
  //   p.dir = newValue;

  //   const newPath = nodePath.format(p);
  //   this.path = newPath;
  // }

  get extname(): string {
    return nodePath.extname(this.path);
  }

  // set extname(newValue: string) {
  //   newValue = normalizeExtName(newValue);
  //   const p = nodePath.parse(this.path);
  //   p.base = ""; // node ignores p.ext and p.name if p.base is provided
  //   p.ext = newValue;

  //   const newPath = nodePath.format(p);
  //   this.path = newPath;
  // }
}

export function parseCode({
  filePathOrName,
  code,
}: {
  filePathOrName: string;
  code: string;
}): Parser.Tree {
  const parser = makeParser({ filePathOrName });
  return parser.parse(code);
}

export function makeParser({
  filePathOrName,
}: {
  filePathOrName: string;
}): Parser {
  const grammar = grammarForFilePathOrName(filePathOrName);
  const parser = new Parser();
  parser.setLanguage(grammar);
  return parser;
}

export function changeFileExtension({
  filePathOrName,
  to,
}: {
  filePathOrName: string;
  to: string;
}): string {
  const p = nodePath.parse(filePathOrName);
  p.base = ""; // node ignores p.ext and p.name if p.base is provided
  p.ext = normalizeExtName(to);
  return nodePath.format(p);
}
