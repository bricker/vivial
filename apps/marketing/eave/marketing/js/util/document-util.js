import { DOC_STATUSES } from "../constants.js";

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
  const processingDocs = [];
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
