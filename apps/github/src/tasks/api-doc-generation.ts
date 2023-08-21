import child_process from "child_process";
import path from "path";
import fs, { stat } from "fs";
import walk from "walkdir";
import OpenAIClient, { formatprompt } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js';

// TODO: use Liam's helpers (pending PR merge)
// Open PR: https://github.com/eave-fyi/eave-monorepo/pull/118/files
import Parser, { Query } from "tree-sitter";
import JavaScript from 'tree-sitter-javascript';
import tsPkg from 'tree-sitter-typescript';

type Declaration = {
  code: string,
  node: Parser.SyntaxNode
}

const tsParser = new Parser();
const { typescript: Typescript, tsx } = tsPkg;
tsParser.setLanguage(Typescript);

const jsParser = new Parser();
jsParser.setLanguage(JavaScript);

// TODO: update types.
// TODO: Determine best way to clone a GitHub repo.
function run(command: string) {
  try {
    child_process.execSync(command);
  } catch (e) {
    // TODO: use logger.
    console.error(`Unable to run command '${command}' due to error ${e}`);
  }
}

// TODO: simplify this shit (go back to regex?)
function findRootFilePath(apiPath: string) {
  let rootFile = "";
  walk.sync(apiPath, (filePath, stats) => {
    if (!rootFile && stats.isFile()) {
      const fileExt = filePath.split('.').pop();

      // TODO: handle js files
      if (fileExt === "ts") {
        const code = fs.readFileSync(filePath, 'utf8');
        const codeLines = code.split("\n");
        const tree = tsParser.parse(code);
        const varQuery = new Query(Typescript, `
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


// TODO (V2): Handle local paths that use aliases (e.g. npm package aliases like @eave-fyi).
// TODO: add support for default exports
// TODO: look into using path.extname
function getLocalFilePath(srcDir: string, relativeFilePath: string): string {
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


function readJSFile(filePath: string): string {
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
};


function findDeclaration(node: Parser.SyntaxNode): (Parser.SyntaxNode|null) {
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
function getDeclarationMap(tree: Parser.Tree): Map<string, Declaration> {
  const declarations = new Map();
  for (const node of tree.rootNode.namedChildren) {
    const declaration = findDeclaration(node);
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


function getLocalImportPaths(tree: Parser.Tree, dirname: string): Map<string, string> {
  const imports = new Map();
  const importNodes = tree.rootNode.descendantsOfType("import_statement");
  for (const node of importNodes) {
    const importName = node.namedChild(0)?.text || "";
    const importPath = node.namedChild(1)?.text || "";
    const localPath = getLocalFilePath(dirname, importPath);
    if (localPath) {
      imports.set(importName, localPath);
    }
  }
  return imports;
}


function buildCode(identifier: string, filePath: string, code: string): string {
  const fileCode = readJSFile(filePath);
  const fileTree = tsParser.parse(fileCode);
  const declarationMap = getDeclarationMap(fileTree);
  const declaration = declarationMap.get(identifier);

  if (declaration) {
    code = (declaration.code + '\n\n' + code);
    const localImportPaths = getLocalImportPaths(fileTree, path.dirname(filePath));
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
          code = buildCode(innerIdentifier, localImportPath, code);
        }
      }
    }
  }
  return code;
}


function getImportMap(tree: Parser.Tree, rootFilePath: string): Map<string, string> {
  const importNodes = tree.rootNode.descendantsOfType('import_statement');
  const importMap = new Map();

  for (const importNode of importNodes) {
    const importInfo = new Map();
    for (const node of importNode.namedChildren) {
      importInfo.set(node.type, node.text);
    }

    const relativeFilePath = importInfo.get('string');
    const localFilePath = getLocalFilePath(path.dirname(rootFilePath), relativeFilePath);
    if (localFilePath) {
      const importIdentifiers = importInfo.get("import_clause").replace(/ |{|}/g, "").split(",");
      for (const importIdentifier of importIdentifiers) {
        const importCode = buildCode(importIdentifier, localFilePath, "");
        importMap.set(importIdentifier, importCode);
      }
    }
  }
  return importMap;
}


// TODO: these maps do a lot of the same thing -- maybe combine.
function getVariableMap(tree: Parser.Tree): Map<string, Parser.SyntaxNode> {
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
function extractExpressAPIEndpoints(rootFilePath: string): Array<string> {

  // TODO: REMOVE !
  if (!rootFilePath.includes('confluence')) {
    return [];
  }


  const apiEndpoints: Array<string> = [];
  const code = readJSFile(rootFilePath);
  const tree = tsParser.parse(code);
  const imports = getImportMap(tree, rootFilePath);
  const variables = getVariableMap(tree);
  const declarations = getDeclarationMap(tree);
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


function guessExpressAPIName(rootDir: string): string {
  const dirName = path.basename(rootDir);
  const apiName = dirName.replace(/[^a-zA-Z0-9]/g, ' ').toUpperCase();
  const apiRegex = new RegExp("API");
  if (apiRegex.test(apiName)) {
    return apiName;
  }
  return apiName + " API";
}







// TODO: dynamically determine language (ts vs js)
async function generateExpressAPIDoc(apiEndpoints: Array<string>): Promise<string> {
  let apiDoc = "";
  for (const apiEndpoint of apiEndpoints) {
    const openaiClient = await OpenAIClient.getAuthedClient();
    const systemPrompt = formatprompt(`
      You will be given a block of TypeScript code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

      Your task is to generate API documentation for the provided Express REST API endpoint.

      Use the following template to format your response:

      ## {description of the API endpoint in 3 words or less}

      \`\`\`
      {HTTP Method} {Path}
      \`\`\`

      {high-level description of what the API endpoint does}

      ### Path Parameters

      **{name}** ({type}) *{optional or required}* - {description}

      ### Example Request

      \`\`\`
      {example request}
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
      {apiEndpoint}
    `);
    const openaiResponse = await openaiClient.createChatCompletion({
      parameters: {
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        model: OpenAIModel.GPT4,
      },
    });
    if (openaiResponse) {
      apiDoc += `${openaiResponse}\n\n<br />\n\n`;
    }
  }
  return apiDoc;
}











// TODO: optimize directory walk.
// TODO: ignore certain directories / files (e.g. node_modules and dot files)
async function documentExpressAPIs(repoPath: string, wikiPath: string) {
  const apis = new Map();
  walk.sync(repoPath, (filePath, stats) => {
    if (stats.isFile()) {
      const fileName = path.basename(filePath);
      if (fileName === "package.json") {
        const requirements = fs.readFileSync(filePath, 'utf8');
        const regex = new RegExp("[\"\']express[\"\']");
        if (regex.test(requirements)) {
          const rootDir = path.dirname(filePath);
          const rootFilePath = findRootFilePath(rootDir);
          if (rootFilePath) {
            const apiEndpoints = extractExpressAPIEndpoints(rootFilePath);
            if (apiEndpoints.length) {
              const apiName = guessExpressAPIName(rootDir);
              apis.set(apiName, apiEndpoints);
            }
          }
        }
      }
    }
  });



  for (const [apiName, apiEndpoints] of apis) {
    const apiDoc = await generateExpressAPIDoc(apiEndpoints);


    console.log(apiDoc);



  }


}


// TODO: this logic should run in an endpoint.
async function main() {
  // TODO: pull repo info dynamically.
  const repoName = "eave-monorepo";

  // TODO: Open PR instead of pushing to wiki.
  const wiki = `https://github.com/eave-fyi/${repoName}.wiki.git`;
  const repo = `https://github.com/eave-fyi/${repoName}.git`;

  const repoPath = `temp/${repoName}`;
  const wikiPath = `temp/${repoName}.wiki`;

  // TODO: we will likely end up cloning repos some other way.
  // run(`mkdir temp && cd temp && git clone ${repo} && git clone ${wiki}`);

  await documentExpressAPIs(repoPath, wikiPath);

  // run(`cd ${wikiPath} && git add . && git commit -m 'Document APIs' && git push`);
  // run(`rm -rf temp`);

  // console.log("✅ Successfully Documented APIs");
}

main()
