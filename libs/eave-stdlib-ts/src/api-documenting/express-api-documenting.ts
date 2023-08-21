import child_process from "child_process";
import path from "path";
import fs, { stat } from "fs";
import walk from "walkdir";
import Parser, { Query } from "tree-sitter";

import { stringToProgrammingLanguage, getExtensionMap } from "../language-mapping.js";
import { grammarForLanguage } from "../parsing/grammars.js";
import OpenAIClient, { formatprompt } from "../transformer-ai/openai.js";
import { OpenAIModel } from '../transformer-ai/models.js';


// TODO: figure out what should be static, private and public
// TODO: strengthen types.
// TODO: move types to another file in this dir.

type Repo = {
  name: string,
  url: string,
  wiki?: {
    name: string,
    url: string,
  }
}

type Declaration = {
  code: string,
  node: Parser.SyntaxNode
}

export class ExpressAPIDocumentor {
  readonly repo: Repo;
  parser: Parser = new Parser();

  constructor(repo: Repo) {
    this.repo = repo;
  }

  // TODO: Determine best way to clone a GitHub repo.
  // TODO: use logger.
  #run(command: string) {
    try {
      child_process.execSync(command);
    } catch (e) {
      console.error(`Unable to run command '${command}' due to error ${e}`);
    }
  }


  #getLanguage(extName: string): (string|null) {
    if (extName === ".ts" || extName === ".tsx") {
      return "typescript";
    }
    if (extName === ".js") {
      return "javascript"
    }
    return null;
  }


  // TODO: simplify this shit (go back to regex?)
  #findRootFilePath(apiDir: string) {
    let rootFile = "";
    walk.sync(apiDir, (filePath, stats) => {
      if (!rootFile && stats.isFile()) {
        const extName = path.extname(filePath);
        const language = this.#getLanguage(extName);
        if (language) {
          const grammar = grammarForLanguage({ language, extName });
          this.parser.setLanguage(grammar);

          const code = fs.readFileSync(filePath, 'utf8');
          const codeLines = code.split("\n");
          const tree = this.parser.parse(code);
          const varQuery = new Query(grammar, `
            (variable_declarator
              value: (expression) @varValue)
          `);

          const varMatches = varQuery.matches(tree.rootNode);
          for (const match of varMatches) {
            for (const capture of match.captures) {
              const line = codeLines[capture.node.startPosition.row];
              const i = capture.node.startPosition.column;
              const varValue = line?.slice(i);
              if (varValue === "express();") {
                rootFile = filePath;
              }
            }
          }
        }
      }
    });
    return rootFile;
  }


  #readFile(filePath: string): string {
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf8');
    }
    if (filePath.endsWith(".js")) {
      const tsFilePath = filePath.slice(0, filePath.length - 2) + "ts";
      if (fs.existsSync(tsFilePath)) {
        return fs.readFileSync(tsFilePath, 'utf8');
      }
    }
    return "";
  }

  // TODO (V2): Handle local paths that use aliases (e.g. npm package aliases like @eave-fyi).
  // TODO: add support for default exports
  // TODO: look into using path.extname
  #getLocalFilePath(srcDir: string, relativeFilePath: string): string {
    let filePath = relativeFilePath.replace(/\'|\"/g, "");
    if ((!filePath.endsWith(".js") && !filePath.endsWith(".ts")) || !filePath.startsWith(".")) {
      return "";
    }
    if (filePath.startsWith("./")) {
      return srcDir + filePath.slice(1);
    }

    let numDirsBack = filePath.match(/\.\.\//g)?.length || 0;
    let currentSrcDir = srcDir;
    while (numDirsBack > 0) {
      const lastSlash = currentSrcDir.lastIndexOf("/");
      currentSrcDir = currentSrcDir.slice(0, lastSlash);
      filePath = filePath.slice(3);
      numDirsBack--;
    }
    return currentSrcDir + "/" + filePath;
  }


  #findDeclaration(node: Parser.SyntaxNode): (Parser.SyntaxNode|null) {
    if (node.type.includes("declaration")) {
      return node;
    }
    if (node.type === "export_statement") {
      for (const child of node.children) {
        if (child.type.includes("declaration")) {
          return child;
        }
      }
    }
    return null;
  }


  // TODO: Store node only -- you can get the code from the node.
  #getDeclarationMap(tree: Parser.Tree): Map<string, Declaration> {
    const declarations = new Map();
    for (const node of tree.rootNode.namedChildren) {
      const declaration = this.#findDeclaration(node);
      if (declaration) {
        const identifier = declaration.firstNamedChild?.text;
        if (identifier) {
          declarations.set(identifier, {
            code: declaration.text,
            node: declaration,
          });
        }
      }
    }
    return declarations;
  }

  #getLocalImportPaths(tree: Parser.Tree, dirname: string): Map<string, string> {
    const imports = new Map();
    const importNodes = tree.rootNode.descendantsOfType("import_statement");
    for (const node of importNodes) {
      const importName = node.namedChild(0)?.text || "";
      const importPath = node.namedChild(1)?.text || "";
      const localPath = this.#getLocalFilePath(dirname, importPath);
      if (localPath) {
        imports.set(importName, localPath);
      }
    }
    return imports;
  }

  #buildCode(identifier: string, filePath: string, code: string): string {
    const fileCode = this.#readFile(filePath);
    const fileTree = this.parser.parse(fileCode);
    const declarationMap = this.#getDeclarationMap(fileTree);
    const declaration = declarationMap.get(identifier);

    if (declaration) {
      code = (declaration.code + '\n\n' + code);
      const localImportPaths = this.#getLocalImportPaths(fileTree, path.dirname(filePath));
      const identifierNodes = declaration.node.descendantsOfType('identifier');
      const identifierSet = new Set();

      for (const node of identifierNodes) {
        if (node.text && (node.text !== identifier)) {
          identifierSet.add(node.text);
        }
      }

      for (const val of identifierSet) {
        const innerIdentifier = (val as string);
        const innerDeclaration = declarationMap.get(innerIdentifier);
        if (innerDeclaration) {
          code = (innerDeclaration.code + '\n\n' + code);
        } else {
          const localImportPath = localImportPaths.get(innerIdentifier);
          if (localImportPath) {
            code = this.#buildCode(innerIdentifier, localImportPath, code);
          }
        }
      }
    }
    return code;
  }

  #getImportMap(tree: Parser.Tree, rootFilePath: string): Map<string, string> {
    const importNodes = tree.rootNode.descendantsOfType('import_statement');
    const importMap = new Map();

    for (const importNode of importNodes) {
      const importInfo = new Map();
      for (const node of importNode.namedChildren) {
        importInfo.set(node.type, node.text);
      }

      const relativeFilePath = importInfo.get('string');
      const localFilePath = this.#getLocalFilePath(path.dirname(rootFilePath), relativeFilePath);
      if (localFilePath) {
        const importIdentifiers = importInfo.get("import_clause").replace(/ |{|}/g, "").split(",");
        for (const importIdentifier of importIdentifiers) {
          const importCode = this.#buildCode(importIdentifier, localFilePath,  "");
          importMap.set(importIdentifier, importCode);
        }
      }
    }
    return importMap;
  }


    // TODO: these maps do a lot of the same thing -- maybe combine.
  #getVariableMap(tree: Parser.Tree): Map<string, Parser.SyntaxNode> {
    const variableNodes = tree.rootNode.descendantsOfType('variable_declarator');
    const variableMap = new Map();

    for (const node of variableNodes) {
      const info = new Map();
      for (const child of node.namedChildren) {
        info.set(child.type, child);
      }
      const identifier = info.get('identifier');
      const callExpression = info.get('call_expression');
      if (identifier && callExpression) {
        variableMap.set(identifier.text, callExpression);
      }
    }
    return variableMap;
  }



  // TODO: Handle case where there is no router.
  #getAPIEndpoints(rootFilePath: string): Array<string> {


    // TODO: REMOVE !
    if (!rootFilePath.includes('confluence')) {
      return [];
    }


    const apiEndpoints: Array<string> = [];
    const code = this.#readFile(rootFilePath);
    const tree = this.parser.parse(code);

    const imports = this.#getImportMap(tree, rootFilePath);
    const variables = this.#getVariableMap(tree);
    const declarations = this.#getDeclarationMap(tree);

    let appIdentifier;
    let routerIdentifier;

    for (const [identifier, node] of variables) {
      if (node.text === "express()") {
        appIdentifier = identifier;
        continue;
      }
      if (node.text.startsWith("express.Router(") || node.text.startsWith("Router(")) {
        routerIdentifier = identifier;
      }
    }

    let baseCode = `import express from 'express';\nconst ${appIdentifier} = express();\n`;
    if (routerIdentifier) {
      baseCode += `const ${routerIdentifier} = express.Router();\n`;
    }

    const callNodes = tree.rootNode.descendantsOfType('call_expression');
    for (const node of callNodes) {
      if (node.text.startsWith(`${appIdentifier}.use`)) {
        baseCode += `${node.text}\n`;
      }

      if (routerIdentifier && node.text.startsWith(`${routerIdentifier}.use`)) {
        const identifierNodes = node.descendantsOfType('identifier');
        const identifierSet = new Set();

        for (const node of identifierNodes) {
          if (node.text && (node.text !== routerIdentifier)) {
            identifierSet.add(node.text);
          }
        }

        let endpoint = `${baseCode}\n`;
        for (const val of identifierSet) {
          const identifier = (val as string);
          if (imports.has(identifier)) {
            endpoint += imports.get(identifier);
            continue;
          }
          if (declarations.has(identifier)) {
            endpoint += declarations.get(identifier);
          }
        }
        endpoint += node.text;
        apiEndpoints.push(endpoint);
      }
    }

    return apiEndpoints;
  }


  #guessExpressAPIName(rootDir: string): string {
    const dirName = path.basename(rootDir);
    const apiName = dirName.replace(/[^a-zA-Z0-9]/g, ' ').toUpperCase();
    const apiRegex = new RegExp("API");
    if (apiRegex.test(apiName)) {
      return apiName;
    }
    return apiName + " API";
  }



  // TODO: optimize directory walk.
  // TODO: ignore certain directories / files (e.g. node_modules and dot files)
  // TODO: cloneRepo method.
  document() {
    let cloneCommand = `mkdir temp && cd temp && git clone ${this.repo.url}`;
    if (this.repo.wiki) {
      cloneCommand += ` && git clone ${this.repo.wiki.url}`
    }

    // this.#run(cloneCommand);

    const apis = new Map();
    walk.sync(`temp/${this.repo.name}`, (filePath, stats) => {
      if (stats.isFile()) {
        const fileName = path.basename(filePath);
        if (fileName === "package.json") {
          const requirements = fs.readFileSync(filePath, 'utf8');
          const regex = new RegExp("[\"\']express[\"\']");
          if (regex.test(requirements)) {
            const rootDir = path.dirname(filePath);
            const rootFilePath = this.#findRootFilePath(rootDir);
            if (rootFilePath) {
              const apiEndpoints = this.#getAPIEndpoints(rootFilePath);
              if (apiEndpoints.length) {
                const apiName = this.#guessExpressAPIName(rootDir);
                apis.set(apiName, apiEndpoints);
              }
            }
          }
        }
      }
    });

    // for (const [apiName, apiEndpoints] of apis) {
      // const apiDoc = await generateExpressAPIDoc(apiEndpoints);
      // console.log(apiDoc);
    // }

    // this.#run(`cd ${repo.wiki.url} && git add . && git commit -m 'Document APIs' && git push`);
    // this.#run(`rm -rf temp`);

    // console.log("✅ Successfully Documented APIs");
  }
}



const repo = {
  name: "eave-monorepo",
  url: "https://github.com/eave-fyi/eave-monorepo.git",
  wiki: {
    name: "eave-monorepo.wiki",
    url: "https://github.com/eave-fyi/eave-monorepo.wiki.git",
  }
}
const apiDocumentor = new ExpressAPIDocumentor(repo);
apiDocumentor.document();
