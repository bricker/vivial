import { DocumentInput } from "../core-api/models/documents.js";
import { ConfluenceDestinationInput } from "../core-api/models/team.js";
import {
  ConfluencePage,
  ConfluenceSearchParamsInput,
  ConfluenceSearchResultWithBody,
  ConfluenceSpace,
  DeleteContentInput,
  UpdateConfluenceContentInput,
} from "./models.js";

export interface GetAvailableSpacesRequestBody {}

export interface GetAvailableSpacesResponseBody {
  confluence_spaces: ConfluenceSpace[];
}

export type SearchContentRequestBody = {
  search_params: ConfluenceSearchParamsInput;
};

export interface SearchContentResponseBody {
  results: ConfluenceSearchResultWithBody[];
}

export type CreateContentRequestBody = {
  confluence_destination: ConfluenceDestinationInput;
  document: DocumentInput;
};

export interface CreateContentResponseBody {
  content: ConfluencePage | null;
}

export type UpdateContentRequestBody = {
  content: UpdateConfluenceContentInput;
};

export interface UpdateContentResponseBody {
  content: ConfluencePage | null;
}

export type DeleteContentRequestBody = {
  content: DeleteContentInput;
};
