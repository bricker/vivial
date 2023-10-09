// @ts-check
import { DOC_STATUSES } from "../constants.js";
import * as Types from "../types.js"; // eslint-disable-line no-unused-vars

/**
 * @type {(documents: Types.GithubDocument[]) => Types.GithubDocument[]}
 */
export function sortAPIDocuments(documents) {
  const docsSortedByLastUpdated = documents.sort((docA, docB) => {
    if (docA.status_updated > docB.status_updated) {
      return -1;
    }
    if (docA.status_updated < docB.status_updated) {
      return 1;
    }
    return 0;
  });

  /** @type {Types.GithubDocument[]} */
  const processingDocs = [];
  /** @type {Types.GithubDocument[]} */
  const processedDocs = [];

  for (const doc of docsSortedByLastUpdated) {
    if (doc.status === DOC_STATUSES.PROCESSING) {
      processingDocs.push(doc);
    } else {
      processedDocs.push(doc);
    }
  }
  return [...processingDocs, ...processedDocs];
}
