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

export type ExpressAPI = {
  name: string;
  endpoints: string[];
};

type ExpressIdentifiers = {
  app?: string;
  router?: string;
};

export function testExpressRootFile({
  fileName,
  fileContent,
}: {
  fileName: string;
  fileContent: string;
}): boolean {
  const extName = path.extname(fileName);
  const language = getProgrammingLanguageByExtension(extName);

  if (!language) {
    // Language isn't supported.
    return false;
  }

  const grammar = grammarForLanguage({ language, extName });
  const parser = new Parser();
  parser.setLanguage(grammar);
  const tree = parser.parse(fileContent);
  const variables = getVariableMap({ tree });

  for (const expressionNode of variables.values()) {
    const children = getNodeChildMap({ node: expressionNode });
    const expression = getExpression({ siblings: children });
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
export function isExpressRouteCall({
  node,
  app,
  router,
}: {
  node: Parser.SyntaxNode;
  app: string;
  router: string;
}): boolean {
  const children = getNodeChildMap({ node });
  const expression = getExpression({ siblings: children });
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
export function getExpressAppIdentifiers({
  tree,
}: {
  tree: Parser.Tree;
}): ExpressIdentifiers {
  const variables = getVariableMap({ tree });
  const identifiers: ExpressIdentifiers = {};

  for (const [identifier, expressionNode] of variables) {
    const children = getNodeChildMap({ node: expressionNode });
    const expression = getExpression({ siblings: children });
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
export function guessExpressAPIName({ apiDir }: { apiDir: string }): string {
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
