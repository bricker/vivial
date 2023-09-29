import { promises as fs } from "node:fs";
import path from "node:path";
import Parser from "tree-sitter";
import { eaveLogger, LogContext } from "../logging.js";
import { grammarForLanguage } from "../parsing/grammars.js";
import {
  getProgrammingLanguageByExtension,
  ProgrammingLanguage,
} from "../programming-langs/language-mapping.js";
import { OpenAIModel } from "../transformer-ai/models.js";
import OpenAIClient, { formatprompt } from "../transformer-ai/openai.js";
import { ExpressRoutingMethod } from "../types.js";
import { CtxArg } from "../requests.js";
import { getExpression, getNodeChildMap, getVariableMap } from "./es-parsing-utility.js";


/**
 * Given a relative file path, returns the full local file path if it exists.
 */
export function getLocalFilePath({
  srcDir,
  relativeFilePath,
}: {
  srcDir: string;
  relativeFilePath: string;
}): string {
  let filePath = relativeFilePath.replace(/'|"/g, "");
  const extName = path.extname(filePath);
  const isSupportedFile = extName === ".js" || extName === ".ts";
  const isLocalFile = filePath.startsWith(".");

  if (isSupportedFile && isLocalFile) {
    if (filePath.startsWith("./")) {
      return srcDir + filePath.slice(1);
    }
    let numDirsUp = filePath.match(/\.\.\//g)?.length || 0;
    let currentDir = srcDir;
    while (numDirsUp > 0) {
      currentDir = currentDir.slice(0, currentDir.lastIndexOf("/"));
      filePath = filePath.slice(3);
      numDirsUp -= numDirsUp;
    }
    return `${currentDir}/${filePath}`;
  }
  return "";
}

/**
 * Assesses the import statements in the given tree and builds a map of the
 * imported declarations that live in the target repo.
 */
export function getLocalImportPaths({
  tree,
  filePath,
}: {
  tree: Parser.Tree;
  filePath: string;
}): Map<string, string> {
  const dirName = path.dirname(filePath);
  const importNodes = tree.rootNode.descendantsOfType("import_statement");
  const importPaths = new Map();

  for (const importNode of importNodes) {
    const children = getNodeChildMap({ node: importNode });
    const importPath = children.get("string")?.text || "";
    const importClause = children.get("import_clause")?.text;
    const importNames = importClause?.replace(/ |{|}/g, "").split(",") || [];

    for (const importName of importNames) {
      const fullFilePath = getLocalFilePath({
        srcDir: dirName,
        relativeFilePath: importPath,
      });
      if (fullFilePath) {
        importPaths.set(importName, fullFilePath);
      }
    }
  }
  return importPaths;
}

/**
 * Assesses the require statements in the given tree and builds a map of the
 * imported declarations that live in the target repo.
 */
export function getLocalRequirePaths({
  tree,
  filePath,
}: {
  tree: Parser.Tree;
  filePath: string;
}): Map<string, string> {
  const dirName = path.dirname(filePath);
  const variables = getVariableMap({ tree });
  const requirePaths = new Map();

  for (const [identifier, expressionNode] of variables) {
    const children = getNodeChildMap({ node: expressionNode });
    const expression = getExpression({ siblings: children });

    if (expression === "require") {
      const args = children.get("arguments");
      const relativeFilePath = args?.firstNamedChild?.text || "";
      const fullFilePath =
        relativeFilePath &&
        getLocalFilePath({ srcDir: dirName, relativeFilePath });
      if (fullFilePath) {
        requirePaths.set(identifier, fullFilePath);
      }
    }
  }
  return requirePaths;
}
