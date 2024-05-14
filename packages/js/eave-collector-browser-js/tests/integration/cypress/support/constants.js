const EAVE_CLIENT_ID = Cypress.env("EAVE_CLIENT_ID");

if (!EAVE_CLIENT_ID) {
  throw new Error("EAVE_CLIENT_ID environment variable must be set for integration tests. See the README for more information.");
}

// TODO: change API route stuff once client JS is updated
export const EAVE_API_ROOT = "http://localhost:3000/";
export const ATOM_INGESTION_ROUTE = "matomo";
export const DUMMY_APP_ROOT = `http://localhost:3300?EAVE_CLIENT_ID=${EAVE_CLIENT_ID}`;
export const ATOM_INTERCEPTION_EVENT_NAME = "atomFired";
