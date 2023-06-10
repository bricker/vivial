import { v4 as uuidv4 } from 'uuid';
import { Request, Response } from 'express';
import { AddOn, HostClient } from 'atlassian-connect-express';
import { CreateContentRequestBody, CreateContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { ConfluencePage,ConfluenceSpace } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { DocumentInput } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/documents.js';
import { getAuthedConnectClient } from './util.js';
import { createPage, getPageByTitle, getPageChildren, getSpaceByKey } from '../confluence-client.js';

export default async function createContent(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const { document, confluence_destination } = <CreateContentRequestBody>req.body;

  // Get the space
  const space = await getSpaceByKey({ client, spaceKey: confluence_destination.space_key });
  if (space === null) {
    eaveLogger.warn({ message: `Space not found for key ${confluence_destination.space_key}`, body: req.body });
    res.status(400);
    return;
  }

  if (!space.homepage) {
    eaveLogger.warn(`Homepage not found for space ${confluence_destination.space_key}`);
    res.status(400);
    return;
  }

  // If this document doesn't have any parents, then it goes in the root of the space.
  // We don't need to (and in fact, shouldn't) do any hierarchy search.
  if (document.parent === undefined) {
    // Get a unique name for the document.
    const resolvedDocumentTitle = await resolveTitleConflict({
      client,
      title: document.title,
      space,
    });

    const page = await createPage({
      client,
      space,
      body: document.content,
      title: resolvedDocumentTitle,
    });
    res.send(page);
    return;
  }

  // Otherwise, if the document has at least one parent, build the hierarchy
  const hierarchy: DocumentInput[] = [];
  let parent: DocumentInput | undefined = document.parent;

  while (parent) {
    hierarchy.unshift(parent);
    parent = parent.parent;
  }

  // Get the pages at the root of the space.
  let currentDir: ConfluencePage | undefined; // undefined is root
  let currentDirId: string | undefined; // We have to track this separately because of hoisting, I think
  let currentDirContent = await getPageChildren({ client, pageId: space.homepage?.id })

  // Figure out where the document goes in the Space hierarchy.
  // For each level in the given hierarchy, check if a page (i.e. folder, same thing) already exists with the given name.
  // If it exists at this level, then we enter it.
  // If it doesn't exist at this level, and doesn't exist anywhere else in the space, then we create it at this level and enter it.
  // If it doesn't exist at this level, but exists somewhere else in the space, then we get a unique name, create it, and enter it.
  // There is almost certainly a better way to do this using the Confluence APIs!

  for (const dir of hierarchy) {
    const existingDirAtThisLevel = currentDirContent.find((content) => content.title === dir.title);
    if (existingDirAtThisLevel !== undefined) {
      // A directory with the given name exists at this level; enter it.
      currentDir = existingDirAtThisLevel;
      currentDirId = String(existingDirAtThisLevel.id);
    } else {
      // A directory with the given name doesn't exist at this level.
      // Call resolveTitleConflict to get a unique name. This accomplishes three things at once:
      // 1. Check if a page with this name exists anywhere else in the space,
      // 1. If no, use the given name
      // 1. If yes, use another, unique name
      // resolveTitleConflict does all of these things and returns the title to use (which may be the given title)
      const resolvedFolderTitle = await resolveTitleConflict({
        client,
        title: dir.title,
        space,
      });
      const newFolderAtThisLevel = await createPage({
        client,
        space,
        title: resolvedFolderTitle,
        body: '', // A "folder" is just an empty page.
        parentId: currentDirId, // If we get here and currentDir is null, it means we're creating a new folder in the root of the space.
      });
      if (newFolderAtThisLevel) {
        // TODO: What happens if createPage returns an error?
        // Now enter the new folder
        currentDir = newFolderAtThisLevel;
        currentDirId = String(newFolderAtThisLevel.id);
      }
    }

    if (currentDir) {
      // TODO: What happens if currentDir is null?
      currentDirContent = await getPageChildren({ client, pageId: String(currentDir.id) });
    }
  }

  // At this point, we're "in" the direct parent directory of the new document.
  // We don't have to worry about title conflicts here, because we already took care of that at the top of this function.
  // TODO: There is a high risk of a race condition where this function is running twice with conflicting data,
  // eg a new document is created with the same title in another request, and then this function will fail because we think that the title is unique.

  // Get a unique name for the document.
  // Note that we're duplicating this code from the top of the function to try to avoid a race condition where a document with the same title is created in another requests,
  // since the hierarchy traversal algorithm above can take a long time to perform.
  // TODO: The race condition still exists; this operation should handle an API error when the page title already exists, and try again with a new title.
  const resolvedDocumentTitle = await resolveTitleConflict({
    client,
    title: document.title,
    space,
  });

  const newDocument = await createPage({
    client,
    space,
    title: resolvedDocumentTitle,
    body: document.content,
    parentId: currentDirId,
  });

  const responseBody: CreateContentResponseBody = {
    content: newDocument,
  };
  res.json(responseBody);
}

async function resolveTitleConflict({ client, title, space }: { client: HostClient, title: string, space: ConfluenceSpace }): Promise<string> {
  // TODO: This can be done "passively", i.e. handle an API response error and then run this function to get a unique title.
  let resolvedTitle = title;
  const limit = 20;
  let n = 0;

  let page = await getPageByTitle({ client, title: resolvedTitle, space });

  while (page) {
    if (n > limit) {
      // failsafe to avoid forever loop. I don't know why this would happen, but it would be a big problem if it did.
      const giveup = uuidv4();
      resolvedTitle = `${title} (${giveup})`;
      break;
    } else {
      n += 1;
      resolvedTitle = `${title} (${n})`;
      page = await getPageByTitle({ client, title: resolvedTitle, space });
    }
  }

  return resolvedTitle;
}
