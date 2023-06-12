import { promisify } from 'util';
import { Request } from 'express';
import { AddOn, HostClient } from 'atlassian-connect-express';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import html from 'html-entities';
import appConfig from '../config.js';


// Fixes some HTML things that Confluence chokes on
export function cleanDocument(document: string): string {
  let content = html.decode(document);
  content = content.replace(/&/g, '&amp;'); // confluence can't handle decoded ampersands
  content = content.replace(/<br>/gi, '<br/>'); // confluence can't handle unclosed br tags
  return content;
}
