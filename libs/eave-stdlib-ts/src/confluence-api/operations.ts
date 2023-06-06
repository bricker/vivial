import { DocumentInput } from "../core-api/models/documents.js";
import { DocumentReferenceInput } from "../core-api/models/subscriptions.js";
import { ConfluenceDestinationInput } from "../core-api/models/team.js";
import { ConfluencePage, ConfluenceSearchParamsInput, ConfluenceSearchResult, ConfluenceSpace, DeleteContentInput } from "./models.js";

export interface GetAvailableSpacesRequestBody {
}

export interface GetAvailableSpacesResponseBody {
  confluence_spaces: ConfluenceSpace[];
}


export type SearchContentRequestBody = {
  search_params: ConfluenceSearchParamsInput;
}

export interface SearchContentResponseBody {
  results: ConfluenceSearchResult[];
}

export type CreateContentRequestBody = {
  confluence_destination: ConfluenceDestinationInput;
  document: DocumentInput;
}

export interface CreateContentResponseBody {
  content: ConfluencePage;
}

export type DeleteContentRequestBody = {
  content: DeleteContentInput;
}
