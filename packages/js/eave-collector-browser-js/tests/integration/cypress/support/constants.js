export const EAVE_CLIENT_ID = Cypress.env("EAVE_CLIENT_ID");
if (!EAVE_CLIENT_ID) {
  throw new Error("EAVE_CLIENT_ID environment variable must be set for integration tests. See the README for more information.");
}

export const EAVE_API_BASE_URL_PUBLIC = Cypress.env("EAVE_API_BASE_URL_PUBLIC") || "http://api.eave.run:8080";
export const EAVE_ATOM_INGESTION_ENDPOINT = `${EAVE_API_BASE_URL_PUBLIC}/public/ingest/browser`;
export const DUMMY_APP_ROOT = `http://localhost:3300?EAVE_CLIENT_ID=${EAVE_CLIENT_ID}&EAVE_ATOM_INGESTION_ENDPOINT=${EAVE_ATOM_INGESTION_ENDPOINT}`;
export const ATOM_INTERCEPTION_EVENT_NAME = "atomFired";
