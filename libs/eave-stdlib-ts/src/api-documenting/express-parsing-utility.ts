import { promises as fs } from "node:fs";
import path from "node:path";
import Parser from "tree-sitter";
import { eaveLogger, LogContext } from "../logging.js";
import { assertPresence, titleize, underscoreify } from "../util.js";
import { grammarForLanguage } from "../parsing/grammars.js";
import {
  getProgrammingLanguageByExtension,
  getProgrammingLanguageByFilePathOrName,
  ProgrammingLanguage,
} from "../programming-langs/language-mapping.js";
import { OpenAIModel } from "../transformer-ai/models.js";
import OpenAIClient, { formatprompt } from "../transformer-ai/openai.js";
import { ExpressRoutingMethod } from "../types.js";
import { CtxArg } from "../requests.js";
import { ESParsingUtility } from "./es-parsing-utility.js";
import { CodeFile } from "./parsing-utility.js";
import { logEvent } from "../analytics.js";

export class ExpressAPI {
  name?: string;
  rootDir?: string
  rootFile?: CodeFile
  endpoints?: string[];
  documentation?: string;

  constructor({ name, rootDir, rootFile, endpoints, documentation }: { name?: string, rootDir?: string, rootFile?: CodeFile, endpoints?: string[], documentation?: string }) {
    this.name = name;
    this.rootDir = rootDir
    this.rootFile = rootFile
    this.endpoints = endpoints
    this.documentation = documentation
  }

  get documentationFilePath(): string {
    assertPresence(this.name);
    const basename = underscoreify(this.name);
    return `eave_docs/${basename}.md`;
  }
}

type ExpressIdentifiers = {
  app?: string;
  router?: string;
};

export class ExpressParsingUtility extends ESParsingUtility {
  testExpressRootFile({
    file
  }: {
    file: CodeFile;
  }): boolean {
    if (!file.language) {
      // Language isn't supported.
      return false;
    }

    const tree = this.parseCode({ file });
    const variables = this.getVariableMap({ tree });

    for (const expressionNode of variables.values()) {
      const children = this.getNodeChildMap({ node: expressionNode });
      const expression = this.getExpression({ siblings: children });
      if (expression === "express") {
        // We think this file initializes an Express server.
        return true;
      }
    }

    // We didn't see an Express server initialized in this file.
    return false;
  }

    /**
   * Returns true if the text for a given node is setting up an Express route.
   * Otherwise, returns false.
   */
  isExpressRouteCall({
    node,
    app,
    router,
  }: {
    node: Parser.SyntaxNode;
    app: string;
    router: string;
  }): boolean {
    const children = this.getNodeChildMap({ node });
    const expression = this.getExpression({ siblings: children });
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
   * Searches a tree for relevant Express calls and returns the variables that
   * are used to declare the root Express app and the Express Router if needed.
   */
  getExpressAppIdentifiers({
    tree,
  }: {
    tree: Parser.Tree;
  }): ExpressIdentifiers {
    const variables = this.getVariableMap({ tree });
    const identifiers: ExpressIdentifiers = {};

    for (const [identifier, expressionNode] of variables) {
      const children = this.getNodeChildMap({ node: expressionNode });
      const expression = this.getExpression({ siblings: children });
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
   * Uses an Express API's root directory name to cobble together a guess for
   * what the name of the API is.
   *
   * NOTE: I kind of hate this. If you are reading this and can think of a
   * better solution, feel free to gently place this code into a trash can.
   */
  guessExpressAPIName({ apiDir }: { apiDir: string }): string {
    const dirName = path.basename(apiDir);
    const apiName = dirName.replace(/[^a-zA-Z0-9]/g, " ").toLowerCase();
    const capitalizedName = titleize(apiName).replace(/ api ?$/ig, "");
    return `${capitalizedName} API`;
  }



  /**
   * Given a list of Express API endpoints, this function builds up API
   * documentation by sending the endpoints to OpenAI one at a time.
   */
  async generateExpressAPIDoc({ api, ctx }: CtxArg & { api: ExpressAPI }): Promise<string | null> {
    let apiDoc = "";
    assertPresence(api.endpoints);
    for (const apiEndpoint of api.endpoints) {
      const openaiClient = await OpenAIClient.getAuthedClient();
      const systemPrompt = formatprompt(`
        You will be given a block of ${api.rootFile?.language || ""} code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

        Your task is to generate API documentation for the provided Express REST API endpoint.

        If the provided code does not contain enough information to generate API documentation, respond with "none"

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
          ctx,
        });

        if (openaiResponse.length === 0 || openaiResponse.match(/^none/)) {
          await logEvent({
            event_name: "express_api_documentation_openai_empty_response",
            event_description:
              "OpenAI couldn't generate documentation for this API",
            event_source: "generateExpressAPIDoc",
            opaque_params: {
              apiName: api.name,
              rootFile: api.rootFile?.path,
              rootDir: api.rootDir,
              language: api.rootFile?.language,
            },
          }, ctx);

          eaveLogger.warning("openAI didn't return API documentation", { openaiResponse }, ctx);
          continue;
        }

        apiDoc += `${openaiResponse}\n\n<br />\n\n`;
      } catch (e: any) {
        eaveLogger.error(e, ctx);
        continue;
      }
    }

    if (apiDoc.length === 0) {
      return null;
    }
    return apiDoc;
  }
}