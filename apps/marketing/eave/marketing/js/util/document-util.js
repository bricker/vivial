// @ts-check
import * as Types from "../types.js"; /**
 * Sorts an array of API documents based on their 'status_updated' property in descending order.
 * Then, it separates the documents into two categories: 'processing' and 'processed'.
 * Finally, it returns a new array with 'processing' documents followed by 'processed' documents.
 *
 * @type {(documents: Types.GithubDocument[]) => Types.GithubDocument[]}
 * @param {Types.GithubDocument[]} documents - The array of documents to be sorted and categorized.
 * @returns {Types.GithubDocument[]} The sorted and categorized array of documents.
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
    if (doc.status === "processing") {
      processingDocs.push(doc);
    } else {
      processedDocs.push(doc);
    }
  }
  return [...processingDocs, ...processedDocs];
}
