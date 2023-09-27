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

const DIR_EXCLUDES = ["node_modules"];

export type Repo = {
  name: string;
  url: string;
  wiki?: {
    name: string;
    url: string;
  };
};

export type ExpressAPI = {
  name: string;
  endpoints: string[];
};

type ExpressIdentifiers = {
  app?: string;
  router?: string;
};

/**
 * Given a link to a GitHub repository, this class can search the repository
 * for Express APIs and generate documentation for those APIs. Example usage:
 *
 * const documentor = new ExpressAPIDocumentor( {
 *   name: "eave-monorepo",
 *   url: "https://github.com/eave-fyi/eave-monorepo.git",
 *   wiki: {
 *     name: "eave-monorepo.wiki",
 *     url: "https://github.com/eave-fyi/eave-monorepo.wiki.git",
 *   }
 * });
 * documentor.document();
 */
export class ExpressAPIDocumentor {
  readonly repo: Repo;

  repoDir = "";

  wikiDir?: string;

  language?: ProgrammingLanguage;

  parser: Parser = new Parser();

  readonly #ctx: LogContext;

  constructor(repo: Repo, ctx: LogContext) {
    this.repo = repo;
    this.#ctx = ctx;
  }

  /**
   * Identifies all Express APIs in a repo associated with an instance of this
   * class and generates API documentation for each API.
   */
  async document({ dir }: { dir: string }) {
    const apis = await this.getExpressAPIs({ dir });
    await Promise.allSettled(
      apis.map(async (api) => {
        await this.#generateExpressAPIDoc({ api });
        // TODO: Open pull request
      }),
    );
  }

  /**
   * Searches package.json files in a repo associated with an instance of this
   * class. If any package file requires Express, this function will drill into the
   * directory that the package file is in and attempt to build Express API code.
   */
  async getExpressAPIs({ dir }: { dir: string }): Promise<ExpressAPI[]> {
    const apis: ExpressAPI[] = [];

    // NOTE: in node 20.1.0, a 'recursive' flag was added. It's not documented but probably useful here.
    const dirents = await fs.readdir(dir, { withFileTypes: true });

    // BFS: First look at the files in the directory, then enter each directory
    await Promise.allSettled(
      dirents
        .filter((d) => d.name === "package.json")
        .map(async (dirent) => {
          const filePath = path.join(dir, dirent.name);
          const fileContents = await fs.readFile(filePath, "utf8");
          try {
            const packageObj = JSON.parse(fileContents);
            if (packageObj.dependencies?.["express"]) {
              const rootFilePath = await this.#findRootFilePath({
                apiDir: dir,
              });
              if (rootFilePath) {
                const apiEndpoints = await this.#getExpressAPIEndpoints({
                  rootFilePath,
                });
                if (apiEndpoints && apiEndpoints.length > 0) {
                  const apiName = this.#guessExpressAPIName({ apiDir: dir });
                  apis.push({ name: apiName, endpoints: apiEndpoints });
                }
              }
            }
          } catch (e: any) {
            eaveLogger.exception(e, this.#ctx);
          }
        }),
    );

    // now enter each directory
    await Promise.allSettled(
      dirents
        .filter((d) => d.isDirectory() && !DIR_EXCLUDES.includes(d.name))
        .map(async (dirent) => {
          const dirPath = path.join(dir, dirent.name);
          const nestedApis = await this.getExpressAPIs({ dir: dirPath });
          apis.push(...nestedApis);
        }),
    );

    return apis;
  }

  /**
   * Given the directory of a suspected Express API, finds the file in which
   * the Express app is initialized.
   */
  async #findRootFilePath({
    apiDir,
  }: {
    apiDir: string;
  }): Promise<string | null> {
    const dirents = await fs.readdir(apiDir, { withFileTypes: true });

    // BFS
    const files = dirents.filter((d) => d.isFile());
    for (const dirent of files) {
      const extName = path.extname(dirent.name);
      const language = getProgrammingLanguageByExtension(extName);
      if (language) {
        this.language = language;
        const grammar = grammarForLanguage({ language, extName });
        this.parser.setLanguage(grammar);

        const filePath = path.join(apiDir, dirent.name);
        const code = await fs.readFile(filePath, "utf8");
        const tree = this.parser.parse(code);
        const variables = this.#getVariableMap({ tree });

        for (const expressionNode of variables.values()) {
          const children = this.#getNodeChildMap({ node: expressionNode });
          const expression = this.#getExpression({ siblings: children });
          if (expression === "express") {
            // We found the file; return from the whole function.
            return filePath;
          }
        }
      }
    }

    const dirs = dirents.filter(
      (d) => d.isDirectory() && !DIR_EXCLUDES.includes(d.name),
    );
    for (const dirent of dirs) {
      const dirPath = path.join(apiDir, dirent.name);
      const rootFilePath = await this.#findRootFilePath({ apiDir: dirPath });
      if (rootFilePath) {
        // A subdirectory had the file; return it.
        return rootFilePath;
      }
    }

    // No file was found. Return null.
    return null;
  }

  /**
   * Given a relative file path, returns the full local file path if it exists.
   */
  #getLocalFilePath({
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
  #getLocalImportPaths({
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
      const children = this.#getNodeChildMap({ node: importNode });
      const importPath = children.get("string")?.text || "";
      const importClause = children.get("import_clause")?.text;
      const importNames = importClause?.replace(/ |{|}/g, "").split(",") || [];

      for (const importName of importNames) {
        const fullFilePath = this.#getLocalFilePath({
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
  #getLocalRequirePaths({
    tree,
    filePath,
  }: {
    tree: Parser.Tree;
    filePath: string;
  }): Map<string, string> {
    const dirName = path.dirname(filePath);
    const variables = this.#getVariableMap({ tree });
    const requirePaths = new Map();

    for (const [identifier, expressionNode] of variables) {
      const children = this.#getNodeChildMap({ node: expressionNode });
      const expression = this.#getExpression({ siblings: children });

      if (expression === "require") {
        const args = children.get("arguments");
        const relativeFilePath = args?.firstNamedChild?.text || "";
        const fullFilePath =
          relativeFilePath &&
          this.#getLocalFilePath({ srcDir: dirName, relativeFilePath });
        if (fullFilePath) {
          requirePaths.set(identifier, fullFilePath);
        }
      }
    }
    return requirePaths;
  }

  /**
   * Adds the given node's children to a map for convenient lookup.
   */
  #getNodeChildMap({
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
  #getVariableMap({
    tree,
  }: {
    tree: Parser.Tree;
  }): Map<string, Parser.SyntaxNode> {
    const variableNodes = tree.rootNode.descendantsOfType(
      "variable_declarator",
    );
    const variables = new Map();
    for (const node of variableNodes) {
      const children = this.#getNodeChildMap({ node });
      const identifierNode = children.get("identifier");
      const expressionNode = children.get("call_expression");
      if (identifierNode && expressionNode) {
        variables.set(identifierNode.text, expressionNode);
      }
    }
    return variables;
  }

  /**
   * Finds the closest declaration node to a given node.
   * If the given node is a declarationn node, it is returned.
   */
  #findDeclaration({
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
   * Given a tree, finds all of the top-level declarations in that tree and
   * returns them in a convenient map.
   */
  #getDeclarationMap({
    tree,
  }: {
    tree: Parser.Tree;
  }): Map<string, Parser.SyntaxNode> {
    const declarations = new Map();
    for (const node of tree.rootNode.namedChildren) {
      const declaration = this.#findDeclaration({ node });
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
   * Given a map of sibling nodes, returns the first expression detected.
   * Use getNodeChildMap(node) to get a map of sibling nodes.
   */
  #getExpression({
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
   * Searches a tree for relevant Express calls and returns the variables that
   * are used to declare the root Express app and the Express Router if needed.
   */
  async #getExpressAppIdentifiers({
    tree,
  }: {
    tree: Parser.Tree;
  }): Promise<ExpressIdentifiers> {
    const variables = await this.#getVariableMap({ tree });
    const identifiers: ExpressIdentifiers = {};

    for (const [identifier, expressionNode] of variables) {
      const children = await this.#getNodeChildMap({ node: expressionNode });
      const expression = await this.#getExpression({ siblings: children });
      if (expression === "express") {
        identifiers.app = identifier;
        continue;
      }
      if (expression === "express.Router" || expression === "Router") {
        identifiers.router = identifier;
      }
    }
    return identifiers;
  }

  /**
   * Given a node, returns the uniqie set of identifiers referenced in that node.
   * Ignores any exclusions passed in.
   */
  #getUniqueIdentifiers({
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
   * Uses an Express API's root directory name to cobble together a guess for
   * what the name of the API is.
   *
   * NOTE: I kind of hate this. If you are reading this and can think of a
   * better solution, feel free to gently place this code into a trash can.
   */
  #guessExpressAPIName({ apiDir }: { apiDir: string }): string {
    const dirName = path.basename(apiDir);
    const apiName = dirName.replace(/[^a-zA-Z0-9]/g, " ").toLowerCase();
    const capitalizedName = apiName.split(" ").map((str) => {
      if (/api/.test(str.toLowerCase())) {
        return "";
      }
      return str && str[0] && str[0].toUpperCase() + str.slice(1);
    });
    return `${capitalizedName.join(" ")} API`;
  }

  /**
   * Returns true if the text for a given node is setting up an Express route.
   * Otherwise, returns false.
   */
  async #isExpressRouteCall({
    node,
    app,
    router,
  }: {
    node: Parser.SyntaxNode;
    app: string;
    router: string;
  }): Promise<boolean> {
    const children = await this.#getNodeChildMap({ node });
    const expression = await this.#getExpression({ siblings: children });
    if (expression) {
      if (router) {
        return expression === `${router}.use`;
      }
      if (expression.startsWith(`${app}.`)) {
        for (const method of Object.values(ExpressRoutingMethod)) {
          if (expression === `${app}.${method}`) {
            return true;
          }
        }
      }
    }
    return false;
  }

  /**
   * Reads the file at the given path if it exists. If the file path ends in .js,
   * it will be converted to a .ts path if needed.
   */
  async #readFile({ filePath }: { filePath: string }): Promise<string | null> {
    try {
      const contents = await fs.readFile(filePath, "utf8");
      return contents;
    } catch (e: any) {
      // eaveLogger.exception(e, this.#ctx);
    }

    // Because typescript source files are imported as js (compiled) files, we need to try to import the js version of the ts file.
    if (path.extname(filePath) === ".js") {
      const tsFilePath = `${filePath.slice(0, filePath.length - 2)}ts`;

      try {
        const contents = await fs.readFile(tsFilePath, "utf8");
        return contents;
      } catch (e: any) {
        eaveLogger.exception(e, this.#ctx);
      }
    }

    // fallback case
    return null;
  }

  /**
   * Given a top-level declaration identifier, this function recursively builds
   * up all of the local source code for that declaration.
   */
  async #buildCode({
    identifier,
    filePath,
    accumulator = "",
  }: {
    identifier: string;
    filePath: string;
    accumulator?: string;
  }): Promise<string | undefined> {
    // Case 1: Required fields are missing.
    if (!identifier || !filePath) {
      return accumulator;
    }

    const code = await this.#readFile({ filePath });
    if (!code) {
      return undefined;
    }

    const tree = this.parser.parse(code);
    const declarations = this.#getDeclarationMap({ tree });
    const declaration = declarations.get(identifier);

    // Case 2: The given identifier is declared in the given file.
    if (declaration) {
      accumulator += `${declaration.text}\n\n`;
      const importPaths = this.#getLocalImportPaths({ tree, filePath });
      const requirePaths = this.#getLocalRequirePaths({ tree, filePath });
      const innerIdentifiers = this.#getUniqueIdentifiers({
        rootNode: declaration,
        exclusions: [identifier],
      });

      for (const innerIdentifier of innerIdentifiers) {
        const innerDeclaration = declarations.get(innerIdentifier);
        const isRequire = innerDeclaration?.text.includes("= require(");
        if (innerDeclaration && !isRequire) {
          accumulator += `${innerDeclaration.text}\n\n`;
          continue;
        }
        const importPath = importPaths.get(innerIdentifier);
        if (importPath) {
          const c = await this.#buildCode({
            identifier: innerIdentifier,
            filePath: importPath,
            accumulator,
          });
          if (c) {
            accumulator = c;
          }
          continue;
        }
        const requirePath = requirePaths.get(innerIdentifier);
        if (requirePath) {
          const c = await this.#buildCode({
            identifier: innerIdentifier,
            filePath: requirePath,
            accumulator,
          });
          if (c) {
            accumulator = c;
          }
        }
      }
      return accumulator;
    }

    // Case 3: The declaration we're looking for wasn't found -- check for default export.
    const exportNodes = tree.rootNode.descendantsOfType("export_statement");
    for (const exportNode of exportNodes) {
      const children = this.#getNodeChildMap({ node: exportNode });
      if (children.has("default")) {
        const defaultIdentifier = children.get("identifier")?.text;
        if (defaultIdentifier) {
          const c = await this.#buildCode({
            identifier: defaultIdentifier,
            filePath,
            accumulator,
          });
          if (c) {
            accumulator = c;
            accumulator = c.replaceAll(defaultIdentifier, identifier);
          }
        }
      }
    }

    return accumulator;
  }

  /**
   * Given a tree, builds the local source code for the top-level imports found
   * in the tree. Returns the code in a map for convenient lookup.
   */
  async #buildLocalImports({
    tree,
    rootFilePath,
  }: {
    tree: Parser.Tree;
    rootFilePath: string;
  }): Promise<Map<string, string>> {
    const importPaths = this.#getLocalImportPaths({
      tree,
      filePath: rootFilePath,
    });
    const imports = new Map();
    for (const [identifier, importPath] of importPaths) {
      const importCode = await this.#buildCode({
        identifier,
        filePath: importPath,
      });
      imports.set(identifier, importCode);
    }
    return imports;
  }

  /**
   * Given a tree, builds the local source code for the top-level required modules
   * found the tree. Returns the code in a map for convenient lookup.
   */
  async #buildLocalRequires({
    tree,
    rootFilePath,
  }: {
    tree: Parser.Tree;
    rootFilePath: string;
  }): Promise<Map<string, string>> {
    const requirePaths = this.#getLocalRequirePaths({
      tree,
      filePath: rootFilePath,
    });
    const requires = new Map();
    for (const [identifier, requirePath] of requirePaths) {
      const requireCode = await this.#buildCode({
        identifier,
        filePath: requirePath,
      });
      requires.set(identifier, requireCode);
    }
    return requires;
  }

  /**
   * Given a list of Express API endpoints, this function builds up API
   * documentation by sending the endpoints to OpenAI one at a time.
   */
  async #generateExpressAPIDoc({ api }: { api: ExpressAPI }): Promise<string> {
    let apiDoc = "";
    for (const apiEndpoint of api.endpoints) {
      const openaiClient = await OpenAIClient.getAuthedClient();
      const systemPrompt = formatprompt(`
        You will be given a block of ${this.language} code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

        Your task is to generate API documentation for the provided Express REST API endpoint.

        If the provided code does not contain enough information to generate API documentation, respond with "none."

        Otherwise, use the following template to format your response:

        ## {description of the API endpoint in 3 words or less}

        \`\`\`
        {HTTP Method} {Path}
        \`\`\`

        {high-level description of what the API endpoint does}

        ### Path Parameters

        **{name}** ({type}) *{optional or required}* - {description}

        ### Example Request

        \`\`\`
        {example request written in JavaScript}
        \`\`\`

        ### Example Response

        \`\`\`
        {example response}
        \`\`\`

        ### Response Codes

        **{response code}**: {explanation of when this response code will be returned}

      `);
      const userPrompt = formatprompt("!!!", apiEndpoint);

      try {
        const openaiResponse = await openaiClient.createChatCompletion({
          parameters: {
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: userPrompt },
            ],
            model: OpenAIModel.GPT4,
            temperature: 0,
          },
        });
        if (openaiResponse && !openaiResponse.match("^none")) {
          apiDoc += `${openaiResponse}\n\n<br />\n\n`;
        }
      } catch (e) {
        console.error(`Unable to parse api endpoint due to error ${e}`);
      }
    }
    return apiDoc;
  }

  /**
   * Given the root file for an Express API, this function attempts to identify
   * each API endpoint in the file. It then builds the code for each endpoint.
   */
  async #getExpressAPIEndpoints({
    rootFilePath,
  }: {
    rootFilePath: string;
  }): Promise<Array<string> | null> {
    const code = await this.#readFile({ filePath: rootFilePath });
    if (!code) {
      return null;
    }

    const tree = this.parser.parse(code);
    const calls = tree.rootNode.descendantsOfType("call_expression");
    const requires = await this.#buildLocalRequires({ tree, rootFilePath });
    const imports = await this.#buildLocalImports({ tree, rootFilePath });
    const declarations = this.#getDeclarationMap({ tree });
    const { app = "", router = "" } = await this.#getExpressAppIdentifiers({
      tree,
    });
    const apiEndpoints: Array<string> = [];

    let baseCode = `import express from 'express';\nconst ${app} = express();\n`;
    if (router) {
      baseCode += `const ${router} = express.Router();\n`;
    }

    for (const call of calls) {
      const isMiddleWareCall = call.text.startsWith(`${app}.use`);
      if (isMiddleWareCall) {
        baseCode += `${call.text}\n`;
      }

      const isRouteCall = await this.#isExpressRouteCall({
        node: call,
        app,
        router,
      });
      if (isRouteCall) {
        let endpointCode = `${baseCode}\n${call.text}\n\n`;
        const nestedIdentifiers = this.#getUniqueIdentifiers({
          rootNode: call,
          exclusions: [app, router],
        });
        for (const identifier of nestedIdentifiers) {
          const importCode = imports.get(identifier);
          if (importCode) {
            endpointCode += importCode;
            continue;
          }
          const requireCode = requires.get(identifier);
          if (requireCode) {
            endpointCode += requireCode;
            continue;
          }
          const declarationCode = declarations.get(identifier)?.text;
          if (declarationCode) {
            endpointCode += `${declarationCode}\n\n`;
          }
        }
        apiEndpoints.push(endpointCode);
      }
    }

    return apiEndpoints;
  }
}
