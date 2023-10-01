import { promises as fs } from "node:fs";
import { CodeFile, ParsingUtility } from "./parsing-utility.js";
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
import { normalizeExtName } from "../util.js";

export class ESParsingUtility extends ParsingUtility {
  /**
   * Assesses the import statements in the given tree and builds a map of the
   * imported declarations that live in the target repo.
   */
  getLocalImportPaths({
    tree,
    file,
  }: {
    tree: Parser.Tree;
    file: CodeFile;
  }): Map<string, string> {
    const importNodes = tree.rootNode.descendantsOfType("import_statement");
    const importPaths = new Map();

    for (const importNode of importNodes) {
      const children = this.getNodeChildMap({ node: importNode });
      const importPath = children.get("string")?.text || "";
      const importClause = children.get("import_clause")?.text;
      const importNames = importClause?.replace(/ |{|}/g, "").split(",") || [];

      for (const importName of importNames) {
        const fullFilePath = this.getLocalFilePath({
          file,
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
  getLocalRequirePaths({
    tree,
    file,
  }: {
    tree: Parser.Tree;
    file: CodeFile;
  }): Map<string, string> {
    const variables = this.getVariableMap({ tree });
    const requirePaths = new Map();

    for (const [identifier, expressionNode] of variables) {
      const children = this.getNodeChildMap({ node: expressionNode });
      const expression = this.getExpression({ siblings: children });

      if (expression === "require") {
        const args = children.get("arguments");
        const relativeFilePath = args?.firstNamedChild?.text || "";
        const fullFilePath =
          relativeFilePath &&
          this.getLocalFilePath({ file, relativeFilePath });
        if (fullFilePath) {
          requirePaths.set(identifier, fullFilePath);
        }
      }
    }
    return requirePaths;
  }
  /**
   * Given a map of sibling nodes, returns the first expression detected.
   * Use getNodeChildMap(node) to get a map of sibling nodes.
   */
  getExpression({
    siblings,
  }: {
    siblings: Map<string, Parser.SyntaxNode>;
  }): string | undefined {
    if (siblings.has("identifier")) {
      return siblings.get("identifier")?.text;
    }
    return siblings.get("member_expression")?.text;
  }

  /**
   * Adds the given node's children to a map for convenient lookup.
   */
  getNodeChildMap({
    node,
  }: {
    node: Parser.SyntaxNode;
  }): Map<string, Parser.SyntaxNode> {
    const nodeInfo = new Map();
    for (const child of node.children) {
      nodeInfo.set(child.type, child);
    }
    return nodeInfo;
  }

  /**
   * Adds variable nodes to a map for convenient lookup.
   * Currently only considers variables that are set to a call expression.
   */
  getVariableMap({
    tree,
  }: {
    tree: Parser.Tree;
  }): Map<string, Parser.SyntaxNode> {
    const variableNodes = tree.rootNode.descendantsOfType(
      "variable_declarator",
    );
    const variables = new Map();
    for (const node of variableNodes) {
      const children = this.getNodeChildMap({ node });
      const identifierNode = children.get("identifier");
      const expressionNode = children.get("call_expression");
      if (identifierNode && expressionNode) {
        variables.set(identifierNode.text, expressionNode);
      }
    }
    return variables;
  }

  /**
   * Given a tree, finds all of the top-level declarations in that tree and
   * returns them in a convenient map.
   */
  getDeclarationMap({
    tree,
  }: {
    tree: Parser.Tree;
  }): Map<string, Parser.SyntaxNode> {
    const declarations = new Map();
    for (const node of tree.rootNode.namedChildren) {
      const declaration = this.findDeclaration({ node });
      if (declaration) {
        const identifier = node.descendantsOfType("identifier")?.at(0);
        if (identifier) {
          declarations.set(identifier.text, declaration);
        }
      }
    }
    return declarations;
  }

  /**
   * Finds the closest declaration node to a given node.
   * If the given node is a declarationn node, it is returned.
   */
  findDeclaration({
    node,
  }: {
    node: Parser.SyntaxNode;
  }): Parser.SyntaxNode | null {
    if (node.type.includes("declaration")) {
      return node;
    }
    if (node.type === "export_statement") {
      for (const child of node.namedChildren) {
        if (child.type.includes("declaration")) {
          return child;
        }
      }
    }
    return null;
  }

  /**
   * Given a node, returns the unique set of identifiers referenced in that node.
   * Ignores any exclusions passed in.
   */
  getUniqueIdentifiers({
    rootNode,
    exclusions,
  }: {
    rootNode: Parser.SyntaxNode;
    exclusions: Array<string>;
  }): Set<string> {
    const identifiers: Set<string> = new Set();
    for (const node of rootNode.descendantsOfType("identifier")) {
      if (!exclusions.includes(node.text)) {
        identifiers.add(node.text);
      }
    }
    return identifiers;
  }
}