import path from 'path';
import fs from 'fs';
import walk from 'walkdir';
import Parser from 'tree-sitter';

import { runSync } from '../util.js';
import { grammarForLanguage } from '../parsing/grammars.js';
import OpenAIClient, { formatprompt } from '../transformer-ai/openai.js';
import { OpenAIModel } from '../transformer-ai/models.js';

const EXPRESS_ROUTING_METHODS = [
  'checkout',
  'copy',
  'delete',
  'get',
  'head',
  'lock',
  'merge',
  'mkactivity',
  'mkcol',
  'move',
  'm-search',
  'notify',
  'options',
  'patch',
  'post',
  'purge',
  'put',
  'report',
  'search',
  'subscribe',
  'trace',
  'unlock',
  'unsubscribe',
];

type Repo = {
  name: string,
  url: string,
  wiki?: {
    name: string,
    url: string,
  }
}

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

  repoDir = '';

  wikiDir?: string;

  language?: string;

  parser: Parser = new Parser();

  constructor(repo: Repo) {
    this.repo = repo;
  }

  /**
   * Finds the closest declaration node to a given node.
   * If the given node is a declarationn node, it is returned.
   */
  static findDeclaration(node: Parser.SyntaxNode): (Parser.SyntaxNode|null) {
    if (node.type.includes('declaration')) {
      return node;
    }
    if (node.type === 'export_statement') {
      for (const child of node.namedChildren) {
        if (child.type.includes('declaration')) {
          return child;
        }
      }
    }
    return null;
  }

  /**
   * Given a map of sibling nodes, returns the first expression detected.
   * Use getNodeChildMap(node) to get a map of sibling nodes.
   */
  static getExpression(siblings: Map<string, Parser.SyntaxNode>): (string|undefined) {
    if (siblings.has('identifier')) {
      return siblings.get('identifier')?.text;
    }
    return siblings.get('member_expression')?.text;
  }

  /**
   * Returns the programming language associated with the given extension.
   * Only TypeScript and JavaScript are supported.
   */
  static getLanguage(extName: string): (string|undefined) {
    if (extName === '.ts' || extName === '.tsx') {
      return 'typescript';
    }
    if (extName === '.js') {
      return 'javascript';
    }
    return '';
  }

  /**
   * Given a relative file path, returns the full local file path if it exists.
   */
  static getLocalFilePath(srcDir: string, relativeFilePath: string): string {
    let filePath = relativeFilePath.replace(/'|"/g, '');
    const extName = path.extname(filePath);
    const isSupportedFile = extName === '.js' || extName === '.ts';
    const isLocalFile = filePath.startsWith('.');

    if (isSupportedFile && isLocalFile) {
      if (filePath.startsWith('./')) {
        return srcDir + filePath.slice(1);
      }
      let numDirsUp = filePath.match(/\.\.\//g)?.length || 0;
      let currentDir = srcDir;
      while (numDirsUp > 0) {
        currentDir = currentDir.slice(0, currentDir.lastIndexOf('/'));
        filePath = filePath.slice(3);
        numDirsUp -= numDirsUp;
      }
      return `${currentDir}/${filePath}`;
    }
    return '';
  }

  /**
   * Assesses the import statements in the given tree and builds a map of the
   * imported declarations that live in the target repo.
   */
  static getLocalImportPaths(tree: Parser.Tree, filePath: string): Map<string, string> {
    const dirName = path.dirname(filePath);
    const importNodes = tree.rootNode.descendantsOfType('import_statement');
    const importPaths = new Map();

    for (const importNode of importNodes) {
      const children = ExpressAPIDocumentor.getNodeChildMap(importNode);
      const importPath = children.get('string')?.text || '';
      const importClause = children.get('import_clause')?.text;
      const importNames = importClause?.replace(/ |{|}/g, '').split(',') || [];

      for (const importName of importNames) {
        const fullFilePath = ExpressAPIDocumentor.getLocalFilePath(dirName, importPath);
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
  static getLocalRequirePaths(tree: Parser.Tree, filePath: string): Map<string, string> {
    const dirName = path.dirname(filePath);
    const variables = ExpressAPIDocumentor.getVariableMap(tree);
    const requirePaths = new Map();

    for (const [identifier, expressionNode] of variables) {
      const children = ExpressAPIDocumentor.getNodeChildMap(expressionNode);
      const expression = ExpressAPIDocumentor.getExpression(children);

      if (expression === 'require') {
        const args = children.get('arguments');
        const relativeFilePath = args?.firstNamedChild?.text || '';
        const fullFilePath = relativeFilePath && ExpressAPIDocumentor.getLocalFilePath(dirName, relativeFilePath);
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
  static getNodeChildMap(node: Parser.SyntaxNode): Map<string, Parser.SyntaxNode> {
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
  static getVariableMap(tree: Parser.Tree): Map<string, Parser.SyntaxNode> {
    const variableNodes = tree.rootNode.descendantsOfType('variable_declarator');
    const variables = new Map();
    for (const node of variableNodes) {
      const children = ExpressAPIDocumentor.getNodeChildMap(node);
      const identifierNode = children.get('identifier');
      const expressionNode = children.get('call_expression');
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
  static getDeclarationMap(tree: Parser.Tree): Map<string, Parser.SyntaxNode> {
    const declarations = new Map();
    for (const node of tree.rootNode.namedChildren) {
      const declaration = ExpressAPIDocumentor.findDeclaration(node);
      if (declaration) {
        const identifier = node.descendantsOfType('identifier')?.at(0);
        if (identifier) {
          declarations.set(identifier.text, declaration);
        }
      }
    }
    return declarations;
  }

  /**
   * Searches a tree for relevant Express calls and returns the variables that
   * are used to declare the root Express app and the Express Router if needed.
   */
  static getExpressAppIdentifiers(tree: Parser.Tree): Map<string, string> {
    const variables = ExpressAPIDocumentor.getVariableMap(tree);
    const identifiers = new Map();
    for (const [identifier, expressionNode] of variables) {
      const children = ExpressAPIDocumentor.getNodeChildMap(expressionNode);
      const expression = ExpressAPIDocumentor.getExpression(children);
      if (expression === 'express') {
        identifiers.set('app', identifier);
        continue;
      }
      if (expression === 'express.Router' || expression === 'Router') {
        identifiers.set('router', identifier);
      }
    }
    return identifiers;
  }

  /**
   * Given a node, returns the uniqie set of identifiers referenced in that node.
   * Ignores any exclusions passed in.
   */
  static getUniqueIdentifiers(rootNode: Parser.SyntaxNode, exclusions: Array<string>): Set<string> {
    const identifiers: Set<string> = new Set();
    for (const node of rootNode.descendantsOfType('identifier')) {
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
  static guessExpressAPIName(apiDir: string): string {
    const dirName = path.basename(apiDir);
    const apiName = dirName.replace(/[^a-zA-Z0-9]/g, ' ').toLowerCase();
    const capitalizedName = apiName.split(' ').map((str) => {
      if (/api/.test(str.toLowerCase())) {
        return '';
      }
      return str && str[0] && str[0].toUpperCase() + str.slice(1);
    });
    return `${capitalizedName.join(' ')} API`;
  }

  /**
   * Returns true if the text for a given node is setting up an Express route.
   * Otherwise, returns false.
   */
  static isExpressRouteCall(node: Parser.SyntaxNode, app: string, router: string): boolean {
    const children = ExpressAPIDocumentor.getNodeChildMap(node);
    const expression = ExpressAPIDocumentor.getExpression(children);
    if (expression) {
      if (router) {
        return expression === `${router}.use`;
      }
      if (expression.startsWith(`${app}.`)) {
        for (const method of EXPRESS_ROUTING_METHODS) {
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
  static readFile(filePath: string): string {
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf8');
    }
    if (path.extname(filePath) === '.js') {
      const tsFilePath = `${filePath.slice(0, filePath.length - 2)}ts`;
      if (fs.existsSync(tsFilePath)) {
        return fs.readFileSync(tsFilePath, 'utf8');
      }
    }
    return '';
  }

  /**
   * Given a top-level declaration identifier, this function recursively builds
   * up all of the local source code for that declaration.
   */
  #buildCode(identifier: string, filePath: string, accumulator: string): string {
    // Case 1: Required fields are missing.
    if (!identifier || !filePath) {
      return accumulator;
    }

    const code = ExpressAPIDocumentor.readFile(filePath);
    const tree = this.parser.parse(code);
    const declarations = ExpressAPIDocumentor.getDeclarationMap(tree);
    const declaration = declarations.get(identifier);

    // Case 2: The given identifier is declared in the given file.
    if (declaration) {
      accumulator += `${declaration.text}\n\n`;
      const importPaths = ExpressAPIDocumentor.getLocalImportPaths(tree, filePath);
      const requirePaths = ExpressAPIDocumentor.getLocalRequirePaths(tree, filePath);
      const innerIdentifiers = ExpressAPIDocumentor.getUniqueIdentifiers(declaration, [identifier]);

      for (const innerIdentifier of innerIdentifiers) {
        const innerDeclaration = declarations.get(innerIdentifier);
        const isRequire = innerDeclaration?.text.includes('= require(');
        if (innerDeclaration && !isRequire) {
          accumulator += `${innerDeclaration.text}\n\n`;
          continue;
        }
        const importPath = importPaths.get(innerIdentifier);
        if (importPath) {
          accumulator = this.#buildCode(innerIdentifier, importPath, accumulator);
          continue;
        }
        const requirePath = requirePaths.get(innerIdentifier);
        if (requirePath) {
          accumulator = this.#buildCode(innerIdentifier, requirePath, accumulator);
        }
      }
      return accumulator;
    }

    // Case 3: The declaration we're looking for wasn't found -- check for default export.
    const exportNodes = tree.rootNode.descendantsOfType('export_statement');
    for (const exportNode of exportNodes) {
      const children = ExpressAPIDocumentor.getNodeChildMap(exportNode);
      if (children.has('default')) {
        const defaultIdentifier = children.get('identifier')?.text;
        if (defaultIdentifier) {
          accumulator = this.#buildCode(defaultIdentifier, filePath, accumulator);
          accumulator = accumulator.replaceAll(defaultIdentifier, identifier);
        }
      }
    }

    return accumulator;
  }

  /**
   * Given a tree, builds the local source code for the top-level imports found
   * in the tree. Returns the code in a map for convenient lookup.
   */
  #buildLocalImports(tree: Parser.Tree, rootFilePath: string): Map<string, string> {
    const importPaths = ExpressAPIDocumentor.getLocalImportPaths(tree, rootFilePath);
    const imports = new Map();
    for (const [identifier, importPath] of importPaths) {
      const importCode = this.#buildCode(identifier, importPath, '');
      imports.set(identifier, importCode);
    }
    return imports;
  }

  /**
   * Given a tree, builds the local source code for the top-level required modules
   * found the tree. Returns the code in a map for convenient lookup.
   */
  #buildLocalRequires(tree: Parser.Tree, rootFilePath: string): Map<string, string> {
    const requirePaths = ExpressAPIDocumentor.getLocalRequirePaths(tree, rootFilePath);
    const requires = new Map();
    for (const [identifier, requirePath] of requirePaths) {
      const requireCode = this.#buildCode(identifier, requirePath, '');
      requires.set(identifier, requireCode);
    }
    return requires;
  }

  /**
   * Uses a child process to clone a GitHub repo associated with an instance
   * of this class.
   */
  #cloneRepo() {
    this.repoDir = `temp/${this.repo.name}`;
    if (this.repo.wiki) {
      this.wikiDir = `temp/${this.repo.wiki.name}`;
      runSync(`mkdir temp && cd temp && git clone ${this.repo.url} && git clone ${this.repo.wiki.url}`);
    } else {
      runSync(`mkdir temp && cd temp && git clone ${this.repo.url}`);
    }
  }

  /**
   * Given the directory of a suspected Express API, finds the file in which
   * the Express app is initialized.
   */
  #findRootFilePath(apiDir: string) {
    let rootFilePath = '';
    walk.sync(apiDir, (filePath, stats) => {
      if (rootFilePath || !stats.isFile()) {
        return;
      }
      const extName = path.extname(filePath);
      const language = ExpressAPIDocumentor.getLanguage(extName);
      if (language) {
        this.language = language;
        const grammar = grammarForLanguage({ language, extName });
        this.parser.setLanguage(grammar);
        const code = fs.readFileSync(filePath, 'utf8');
        const tree = this.parser.parse(code);
        const variables = ExpressAPIDocumentor.getVariableMap(tree);

        for (const expressionNode of variables.values()) {
          const children = ExpressAPIDocumentor.getNodeChildMap(expressionNode);
          const expression = ExpressAPIDocumentor.getExpression(children);
          if (expression === 'express') {
            rootFilePath = filePath;
          }
        }
      }
    });
    return rootFilePath;
  }

  /**
   * Given a list of Express API endpoints, this function builds up API
   * documentation by sending the endpoints to OpenAI one at a time.
   */
  async #generateExpressAPIDoc(apiEndpoints: Array<string>): Promise<string> {
    let apiDoc = '';
    for (const apiEndpoint of apiEndpoints) {
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
      const userPrompt = formatprompt(`
        !!!
        ${apiEndpoint}
      `);
      try {
        const openaiResponse = await openaiClient.createChatCompletion({
          parameters: {
            messages: [
              { role: 'system', content: systemPrompt },
              { role: 'user', content: userPrompt },
            ],
            model: OpenAIModel.GPT4,
            temperature: 0,
          },
        });
        if (openaiResponse && openaiResponse !== 'none') {
          apiDoc += `${openaiResponse}\n\n<br />\n\n`;
        }
      } catch (e) {
        console.error(`❗ Unable to parse api endpoint due to error ${e}`);
      }
    }
    return apiDoc;
  }

  /**
   * Given the root file for an Express API, this function attempts to identify
   * each API endpoint in the file. It then builds the code for each endpoint.
   */
  #getExpressAPIEndpoints(rootFilePath: string): Array<string> {
    const code = ExpressAPIDocumentor.readFile(rootFilePath);
    const tree = this.parser.parse(code);
    const calls = tree.rootNode.descendantsOfType('call_expression');
    const requires = this.#buildLocalRequires(tree, rootFilePath);
    const imports = this.#buildLocalImports(tree, rootFilePath);
    const declarations = ExpressAPIDocumentor.getDeclarationMap(tree);
    const identifiers = ExpressAPIDocumentor.getExpressAppIdentifiers(tree);
    const app = identifiers.get('app') || '';
    const router = identifiers.get('router') || '';
    const apiEndpoints: Array<string> = [];

    let baseCode = `import express from 'express';\nconst ${app} = express();\n`;
    if (router) baseCode += `const ${router} = express.Router();\n`;

    for (const call of calls) {
      const isMiddleWareCall = call.text.startsWith(`${app}.use`);
      if (isMiddleWareCall) {
        baseCode += `${call.text}\n`;
      }

      const isRouteCall = ExpressAPIDocumentor.isExpressRouteCall(call, app, router);
      if (isRouteCall) {
        let endpointCode = `${baseCode}\n${call.text}\n\n`;
        const nestedIdentifiers = ExpressAPIDocumentor.getUniqueIdentifiers(call, [app, router]);
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

  /**
   * Searches package.json files in a repo associated with an instance of this
   * class. If any package file requires Express, this function will drill into the
   * directory that the package file is in and attempt to build Express API code.
   */
  #getExpressAPIs(): Map<string, Array<string>> {
    const apis = new Map();
    walk.sync(this.repoDir, (filePath, stats) => {
      const isPackageFile = stats.isFile() && (path.basename(filePath) === 'package.json');
      if (isPackageFile) {
        const packageObj = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const usesExpress = packageObj.dependencies?.express;
        if (usesExpress) {
          const rootDir = path.dirname(filePath);
          const rootFilePath = this.#findRootFilePath(rootDir);
          if (rootFilePath) {
            const apiEndpoints = this.#getExpressAPIEndpoints(rootFilePath);
            if (apiEndpoints.length) {
              const apiName = ExpressAPIDocumentor.guessExpressAPIName(rootDir);
              apis.set(apiName, apiEndpoints);
            }
          }
        }
      }
    });
    return apis;
  }

  /**
   * Uses a child process to push an API document to a GitHub Wiki associated
   * with an instance of this class.
   */
  #pushToWiki(apiName: string, apiDoc: string) {
    const filePath = `${this.wikiDir}/${apiName}.md`;
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    fs.appendFileSync(filePath, apiDoc);
    runSync(`cd ${this.wikiDir} && git add . && git commit -m 'Update ${apiName} document.' && git push`);
    console.log(`✅ Successfully documented ${apiName}.`);
  }

  /**
   * Identifies all Express APIs in a repo associated with an instance of this
   * class and generates API documentation for each API.
   */
  async document() {
    this.#cloneRepo();
    const apis = this.#getExpressAPIs();
    for (const [apiName, apiEndpoints] of apis) {
      const apiDoc = await this.#generateExpressAPIDoc(apiEndpoints);
      if (this.repo.wiki) {
        this.#pushToWiki(apiName, apiDoc);
      }
    }
    runSync('rm -rf temp');
  }
}
