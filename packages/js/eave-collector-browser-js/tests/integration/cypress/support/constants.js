export const EAVE_CLIENT_ID = Cypress.env("EAVE_CLIENT_ID");
export const EAVE_API_BASE_URL_PUBLIC = Cypress.env("EAVE_API_BASE_URL_PUBLIC") || "http://api.eave.run:8080";
export const EAVE_ATOM_INGESTION_ENDPOINT = `${EAVE_API_BASE_URL_PUBLIC}/public/ingest/browser`;
export const ATOM_INTERCEPTION_EVENT_NAME = "atomFired";

export function dummyAppRoot({ path, qp } = { path: "/", qp: "" }) {
  return `http://localhost:3300${path}?${qp}`;
}