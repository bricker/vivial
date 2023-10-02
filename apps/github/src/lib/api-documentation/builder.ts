import { ExpressAPI } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import { GithubAPIHelperMixin } from "./github-api.js";
import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import assert from "assert";
import { CoreAPIHelperMixin } from "./core-api.js";
import Parser from "tree-sitter";
import { CodeFile } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/parsing-utility.js";
import { ExpressAPIDocumentorBase } from "./base.js";

export function DocumentBuilderMixin<TBase extends APIHelpersMixin()>(Base: TBase) {
  return class extends Base {
    async getExpressApiInfo({ rootDir, team, eaveRepo, repo, octokit, parser, ctx }: GithubApiCallerArgs & { team: Team, eaveRepo: GithubRepo, rootDir: string }): Promise<ExpressAPI | null> {
      const fwdArgs = { repo, octokit, parser, ctx };

      const api = new ExpressAPI({
        rootDir,
      });

      const expressApiRootFile = await this.getExpressAPIRootFile({ apiRootDir: rootDir, ...fwdArgs });
      if (!expressApiRootFile) {
        // We thought this dir contained an Express app, but couldn't find a file that initialized the express server.
        await logEvent({
          event_name: "express_api_detection_false_positive",
          event_description:
            "An express API was detected, but no root file was found.",
          eave_team: team,
          event_source: "github app",
          opaque_params: {
            repo,
            eaveRepo,
            rootDir,
          },
        }, ctx);

        eaveLogger.warning("No express API root file found", { rootDir }, repo, eaveRepo, ctx);
        return null;
      }
      assert(expressApiRootFile.path, "unexpected missing path property");

      api.rootFile = expressApiRootFile;

      const apiName = await parser.guessExpressAPIName({ apiDir: rootDir });
      api.name = apiName;
      return api;
    }

    /**
     * Given the root file for an Express API, this function attempts to identify
     * each API endpoint in the file. It then builds the code for each endpoint.
     */
    async getExpressAPIEndpoints({
      apiRootFilePath,
      parser,
      repo, octokit, ctx
    }: GithubApiCallerArgs & {
      apiRootFilePath: string;
    }): Promise<Array<string> | null> {
      const fwdArgs = { repo, octokit, ctx, parser };

      const apiRootFile = await this.getFileContent({ filePath: apiRootFilePath, ...fwdArgs });
      assert(apiRootFile, "unexpected missing file object");

      const tree = parser.parseCode({ file: apiRootFile });
      const calls = tree.rootNode.descendantsOfType("call_expression");
      const requires = await this.buildLocalRequires({ tree, file: apiRootFile, ...fwdArgs });
      const imports = await this.buildLocalImports({ tree, file: apiRootFile, ...fwdArgs });
      const declarations = parser.getDeclarationMap({ tree });
      const { app = "", router = "" } = await parser.getExpressAppIdentifiers({
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

        const isRouteCall = await parser.isExpressRouteCall({
          node: call,
          app,
          router,
        });
        if (isRouteCall) {
          let endpointCode = `${baseCode}\n${call.text}\n\n`;
          const nestedIdentifiers = parser.getUniqueIdentifiers({
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
    async buildExpressCode({
      identifier,
      filePath,
      accumulator = "",
      repo,
      octokit,
      ctx,
      parser,
    }: GithubApiCallerArgs & {
      identifier: string;
      filePath: string;
      accumulator?: string;
    }): Promise<string | null> {
      const fwdArgs = { repo, octokit, ctx, parser };
      assert(filePath, "unexpected missing filePath");
      assert(identifier, "unexpected missing identifier");

      const file = await this.getFileContent({ filePath, ...fwdArgs });
      assert(file, "unexpected missing file object");

      const tree = parser.parseCode({ file });
      const declarations = parser.getDeclarationMap({ tree });
      const declaration = declarations.get(identifier);

      // Case 2: The given identifier is declared in the given file.
      if (declaration) {
        accumulator += `${declaration.text}\n\n`;
        const importPaths = parser.getLocalImportPaths({ tree, file });
        const requirePaths = parser.getLocalRequirePaths({ tree, file });
        const innerIdentifiers = parser.getUniqueIdentifiers({
          rootNode: declaration,
          exclusions: [identifier],
        });

        for (const innerIdentifier of innerIdentifiers) {
          const innerDeclaration = declarations.get(innerIdentifier);
          const isRequire = innerDeclaration?.text.match(/require\(["|'][^"|']["|']\)/);
          if (innerDeclaration && !isRequire) {
            accumulator += `${innerDeclaration.text}\n\n`;
            continue;
          }
          const importPath = importPaths.get(innerIdentifier);
          if (importPath) {
            const c = await this.buildExpressCode({
              identifier: innerIdentifier,
              filePath: importPath,
              accumulator,
              ...fwdArgs,
            });
            if (c) {
              accumulator = c;
            }
            continue;
          }
          const requirePath = requirePaths.get(innerIdentifier);
          if (requirePath) {
            const c = await this.buildExpressCode({
              identifier: innerIdentifier,
              filePath: requirePath,
              accumulator,
              ...fwdArgs,
            });
            if (c) {
              accumulator = c;
            }
          }
        }
        return accumulator;
      }

      // FIXME: This is broken (filePath being passed into recursive func
      // // Case 3: The declaration we're looking for wasn't found -- check for default export.
      // const exportNodes = tree.rootNode.descendantsOfType("export_statement");
      // for (const exportNode of exportNodes) {
      //   const children = parser.getNodeChildMap({ node: exportNode });
      //   if (children.has("default")) {
      //     const defaultIdentifier = children.get("identifier")?.text;
      //     if (defaultIdentifier) {
      //       const c = await buildExpressCode({
      //         identifier: defaultIdentifier,
      //         filePath,
      //         accumulator,
      //         ...fwdArgs,
      //       });
      //       if (c) {
      //         accumulator = c;
      //         accumulator = c.replaceAll(defaultIdentifier, identifier);
      //       }
      //     }
      //   }
      // }

      return accumulator;
    }

    /**
     * Given a tree, builds the local source code for the top-level imports found
     * in the tree. Returns the code in a map for convenient lookup.
     */
    async buildLocalImports({
      tree,
      file,
      repo, octokit, ctx, parser
    }: GithubApiCallerArgs & {
      tree: Parser.Tree;
      file: CodeFile;
    }): Promise<Map<string, string>> {
      const fwdArgs = { repo, octokit, ctx, parser };
      const importPaths = parser.getLocalImportPaths({
        tree,
        file,
      });
      const imports = new Map();
      for (const [identifier, importPath] of importPaths) {
        const importCode = await this.buildExpressCode({
          identifier,
          filePath: importPath,
          ...fwdArgs,
        });
        imports.set(identifier, importCode);
      }
      return imports;
    }

    /**
     * Given a tree, builds the local source code for the top-level required modules
     * found the tree. Returns the code in a map for convenient lookup.
     */
    async buildLocalRequires({
      tree,
      file,
      repo, octokit, ctx, parser,
    }: GithubApiCallerArgs & {
      tree: Parser.Tree;
      file: CodeFile;
    }): Promise<Map<string, string>> {
      const fwdArgs = { repo, octokit, parser, ctx };
      const requirePaths = parser.getLocalRequirePaths({
        tree,
        file,
      });
      const requires = new Map();
      for (const [identifier, requirePath] of requirePaths) {
        const requireCode = await this.buildExpressCode({
          identifier,
          filePath: requirePath,
          ...fwdArgs,
        });
        requires.set(identifier, requireCode);
      }
      return requires;
    }
  }
}
