import path from "node:path";
import Parser from "tree-sitter";
import { CodeFile } from "./parsing-utility.js";

export class ESCodeFile extends CodeFile {
  private __memo_variableMap__?: Map<string, Parser.SyntaxNode>;
  private __memo_declarationMap__?: Map<string, Parser.SyntaxNode>;
  private __memo_localImportPaths__?: Map<string, string>;
  private __memo_localRequirePaths__?: Map<string, string>;

  /**
   * Adds variable nodes to a map for convenient lookup.
   * Currently only considers variables that are set to a call expression.
   */
  getVariableMap(): Map<string, Parser.SyntaxNode> {
    if (this.__memo_variableMap__ !== undefined) {
      return this.__memo_variableMap__;
    }

    const variableNodes = this.tree.rootNode.descendantsOfType(
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
    this.__memo_variableMap__ = variables;
    return this.__memo_variableMap__;
  }

  /**
   * Assesses the import statements in the given tree and builds a map of the
   * imported declarations that live in the target repo.
   */
  getLocalImportPaths(): Map<string, string> {
    if (this.__memo_localImportPaths__ !== undefined) {
      return this.__memo_localImportPaths__;
    }

    const importNodes =
      this.tree.rootNode.descendantsOfType("import_statement");
    const importPaths = new Map();

    for (const importNode of importNodes) {
      const children = this.getNodeChildMap({ node: importNode });
      const importPath = children.get("string")?.text || "";
      const importClause = children.get("import_clause")?.text;
      const importNames =
        importClause
          ?.replace(/[\s{}]/g, "")
          .split(",")
          .filter((s) => s) || [];

      for (const importName of importNames) {
        const fullFilePath = this.resolveRelativeFilePath({
          relativeFilePath: importPath,
        });
        if (fullFilePath) {
          importPaths.set(importName, fullFilePath);
        }
      }
    }

    this.__memo_localImportPaths__ = importPaths;
    return this.__memo_localImportPaths__;
  }

  /**
   * Assesses the require statements in the given tree and builds a map of the
   * imported declarations that live in the target repo.
   */
  getLocalRequirePaths(): Map<string, string> {
    if (this.__memo_localRequirePaths__ !== undefined) {
      return this.__memo_localRequirePaths__;
    }
    const variables = this.getVariableMap();
    const requirePaths = new Map();

    for (const [identifier, expressionNode] of variables) {
      const children = this.getNodeChildMap({ node: expressionNode });
      const expression = this.getExpression({ siblings: children });

      if (expression === "require") {
        const args = children.get("arguments");
        const relativeFilePath = args?.firstNamedChild?.text || "";
        const fullFilePath =
          relativeFilePath &&
          this.resolveRelativeFilePath({ relativeFilePath });
        if (fullFilePath) {
          requirePaths.set(identifier, fullFilePath);
        }
      }
    }

    this.__memo_localRequirePaths__ = requirePaths;
    return this.__memo_localRequirePaths__;
  }

  /**
   * Given a tree, finds all of the top-level declarations in that tree and
   * returns them in a convenient map.
   */
  getDeclarationMap(): Map<string, Parser.SyntaxNode> {
    if (this.__memo_declarationMap__ !== undefined) {
      return this.__memo_declarationMap__;
    }

    const declarations = new Map();
    for (const node of this.tree.rootNode.namedChildren) {
      const declaration = this.findDeclaration({ node });
      if (declaration) {
        const identifier = node.descendantsOfType("identifier")?.at(0);
        if (identifier) {
          declarations.set(identifier.text, declaration);
        }
      }
    }

    this.__memo_declarationMap__ = declarations;
    return this.__memo_declarationMap__;
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

  /**
   * Given a relative file path, returns the full local file path if it exists.
   */
  resolveRelativeFilePath({
    relativeFilePath,
  }: {
    relativeFilePath: string;
  }): string {
    relativeFilePath = relativeFilePath.replace(/'|"/g, "");
    const isSupportedFile = this.extname === ".js" || this.extname === ".ts";

    // Don't use path.isAbsolute() here because we're checking node imports, which likely won't start with a /
    const isLocal = relativeFilePath.at(0) === ".";
    if (!isSupportedFile || !isLocal) {
      return "";
    }

    const fullPath = `${this.path}/../${relativeFilePath}`;
    return path.normalize(fullPath);
  }
}
