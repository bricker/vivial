import {
  ExpressAPI,
  ExpressCodeFile,
} from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { changeFileExtension } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/parsing-utility.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { ProgrammingLanguage } from "@eave-fyi/eave-stdlib-ts/src/programming-langs/language-mapping.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import { assertIsBlob } from "../graphql-util.js";
import { GithubAPIData } from "./github-api.js";

export class ExpressAPIDocumentBuilder {
  private readonly githubAPIData: GithubAPIData;
  private readonly ctx: LogContext;
  private readonly apiRootFile: ExpressCodeFile;

  static async buildAPI({
    githubAPIData,
    ctx,
    apiRootDir,
  }: CtxArg & {
    githubAPIData: GithubAPIData;
    apiRootDir: string;
  }): Promise<ExpressAPI> {
    const apiInfo = new ExpressAPI({
      externalRepoId: githubAPIData.externalGithubRepo.id,
      rootDir: apiRootDir,
    });

    for await (const treeEntry of githubAPIData.recurseGitTree({
      treeRootDir: apiRootDir,
    })) {
      const blob = treeEntry.object;
      assertIsBlob(blob);
      if (!blob.text) {
        // text is either null (binary object), undefined (not in response), or empty string (empty file). Either way, move on.
        continue;
      }

      assertPresence(treeEntry.path);
      const file = new ExpressCodeFile({
        path: treeEntry.path,
        contents: blob.text,
      });
      if (file.testExpressRootFile()) {
        // We found the file; Early-exit the loop
        apiInfo.rootFile = file;
        break;
      }
    }

    if (!apiInfo.rootFile) {
      eaveLogger.warning("No express API root file found", { apiRootDir }, ctx);
      return apiInfo;
    }

    const builder = new ExpressAPIDocumentBuilder({
      apiRootFile: apiInfo.rootFile,
      githubAPIData,
      ctx,
    });
    const endpoints = await builder.findExpressAPIEndpoints();

    if (endpoints.length === 0) {
      eaveLogger.warning(
        "No express API endpoints found",
        { apiRootDir, apiRootFile: apiInfo.rootFile?.asJSON },
        ctx,
      );
    }

    return apiInfo;
  }

  private constructor({
    apiRootFile,
    githubAPIData,
    ctx,
  }: CtxArg & { apiRootFile: ExpressCodeFile; githubAPIData: GithubAPIData }) {
    this.githubAPIData = githubAPIData;
    this.ctx = ctx;
    this.apiRootFile = apiRootFile;
  }

  /**
   * Given the root file for an Express API, this function attempts to identify
   * each API endpoint in the file. It then builds the code for each endpoint.
   */
  private async findExpressAPIEndpoints(): Promise<Array<string>> {
    const calls =
      this.apiRootFile.tree.rootNode.descendantsOfType("call_expression");
    const requires = await this.buildLocalRequires();
    const imports = await this.buildLocalImports();
    const declarations = this.apiRootFile.getDeclarationMap();
    const { app = "", router = "" } =
      await this.apiRootFile.getExpressAppIdentifiers();
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

      const isRouteCall = await this.apiRootFile.testExpressRouteCall({
        node: call,
        app,
        router,
      });
      if (isRouteCall) {
        let endpointCode = `${baseCode}\n${call.text}\n\n`;
        const nestedIdentifiers = this.apiRootFile.getUniqueIdentifiers({
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

  /**
   * Given a top-level declaration identifier, this function recursively builds
   * up all of the local source code for that declaration.
   */
  private async concatenateImports({
    identifier,
    expressCodeFile,
  }: {
    identifier: string;
    expressCodeFile: ExpressCodeFile;
  }): Promise<string> {
    const declarations = expressCodeFile.getDeclarationMap();
    const declaration = declarations.get(identifier);

    let accumulator = "";

    // Case 2: The given identifier is declared in the given file.
    if (declaration) {
      accumulator += `${declaration.text}\n\n`;
      const importPaths = expressCodeFile.getLocalImportPaths();
      const requirePaths = expressCodeFile.getLocalRequirePaths();
      const innerIdentifiers = expressCodeFile.getUniqueIdentifiers({
        rootNode: declaration,
        exclusions: [identifier],
      });

      for (const innerIdentifier of innerIdentifiers) {
        const innerDeclaration = declarations.get(innerIdentifier);
        const isRequire = innerDeclaration?.text.match(
          /require\(["|'][^"|']["|']\)/,
        );
        if (innerDeclaration && !isRequire) {
          accumulator += `${innerDeclaration.text}\n\n`;
          continue;
        }
        const importPath = importPaths.get(innerIdentifier);
        if (importPath) {
          const importedFile = await this.getExpressCodeFile({
            filePath: importPath,
          });
          const c = await this.concatenateImports({
            identifier: innerIdentifier,
            expressCodeFile: importedFile,
          });
          accumulator += c;
          continue;
        }
        const requirePath = requirePaths.get(innerIdentifier);
        if (requirePath) {
          const importedFile = await this.getExpressCodeFile({
            filePath: requirePath,
          });
          const c = await this.concatenateImports({
            identifier: innerIdentifier,
            expressCodeFile: importedFile,
          });
          accumulator += c;
        }
      }
      return accumulator;
    }

    // Case 3: The declaration we're looking for wasn't found -- check for default export.
    const exportNodes =
      expressCodeFile.tree.rootNode.descendantsOfType("export_statement");
    for (const exportNode of exportNodes) {
      const children = expressCodeFile.getNodeChildMap({ node: exportNode });
      if (children.has("default")) {
        const defaultIdentifier = children.get("identifier")?.text;
        if (defaultIdentifier) {
          const c = await this.concatenateImports({
            identifier: defaultIdentifier,
            expressCodeFile,
          });
          accumulator += c.replaceAll(defaultIdentifier, identifier);
        }
      }
    }

    return accumulator;
  }

  /**
   * Given a tree, builds the local source code for the top-level imports found
   * in the tree. Returns the code in a map for convenient lookup.
   */
  private async buildLocalImports(): Promise<Map<string, string>> {
    const importPaths = this.apiRootFile.getLocalImportPaths();
    const imports = new Map();
    for (const [identifier, importPath] of importPaths) {
      const expressCodeFile = await this.getExpressCodeFile({
        filePath: importPath,
      });
      const importCode = await this.concatenateImports({
        identifier,
        expressCodeFile,
      });
      imports.set(identifier, importCode);
    }
    return imports;
  }

  /**
   * Given a tree, builds the local source code for the top-level required modules
   * found the tree. Returns the code in a map for convenient lookup.
   */
  private async buildLocalRequires(): Promise<Map<string, string>> {
    const requirePaths = this.apiRootFile.getLocalRequirePaths();
    const requires = new Map();
    for (const [identifier, requirePath] of requirePaths) {
      const expressCodeFile = await this.getExpressCodeFile({
        filePath: requirePath,
      });
      const requireCode = await this.concatenateImports({
        identifier,
        expressCodeFile,
      });
      requires.set(identifier, requireCode);
    }
    return requires;
  }

  private async getExpressCodeFile({
    filePath,
  }: {
    filePath: string;
  }): Promise<ExpressCodeFile> {
    const file = new ExpressCodeFile({ path: filePath, contents: "" }); // empty contents as placeholder

    let gitBlob = await this.githubAPIData.getFileContent({ filePath });
    if (
      !gitBlob &&
      this.apiRootFile.language === ProgrammingLanguage.javascript
    ) {
      // either the file doesn't exist, or this is a javascript import and the source file is typescript.
      const tsFilePath = changeFileExtension({
        filePathOrName: filePath,
        to: ".ts",
      });
      gitBlob = await this.githubAPIData.getFileContent({
        filePath: tsFilePath,
      });
    }

    assertPresence(gitBlob?.text);
    file.contents = gitBlob.text;
    return file;
  }
}
