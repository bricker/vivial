import html from "html-entities";
import ConfluenceClient from "../confluence-client.js";

// Fixes some HTML things that Confluence chokes on
export function cleanDocument(document: string): string {
  let content = html.decode(document);
  content = content.replace(/&/g, "&amp;"); // confluence can't handle decoded ampersands
  content = content.replace(/<br>/gi, "<br/>"); // confluence can't handle unclosed br tags
  return content;
}

export type ConfluenceClientArg = {
  confluenceClient: ConfluenceClient;
};
