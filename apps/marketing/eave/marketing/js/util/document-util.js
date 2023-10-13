// @ts-check
import * as Types from "../types.js"; Here is the merged JavaScript doc comment:

```javascript
/**
 * Sorts an array of API documents based on their update status and separates them into two categories: processing and processed.
 * The documents are first sorted by their 'status_updated' property in descending order.
 * Then, they are divided into two arrays: 'processingDocs' for documents with a 'status' of 'processing', and 'processedDocs' for all other documents.
 * Finally, the function returns a new array that concatenates 'processingDocs' and 'processedDocs', in that order.
 *
 * @type {(documents: Types.GithubDocument[]) => Types.GithubDocument[]}
 * @param {Types.GithubDocument[]} documents - The array of documents to be sorted and categorized.
 * @returns {Types.GithubDocument[]} The sorted and categorized array of documents.
 */
```
This comment maintains the important information from both the old and new documentation. It includes the detailed description of the function's behavior from the new documentation, as well as the type annotation from the old documentation.
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
