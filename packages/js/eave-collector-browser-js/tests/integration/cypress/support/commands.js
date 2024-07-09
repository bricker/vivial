// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

import { ATOM_INTERCEPTION_EVENT_NAME, EAVE_ATOM_INGESTION_ENDPOINT } from "./constants";

/**
 * This intercept helper MUST be called before the atoms we want to intercept are fired,
 * including the pageView ones fired on cy.visit.
 */
Cypress.Commands.add("interceptAtomIngestion", () => {
  // Intercept the ingestion request and mock resp.
  // wildcard at end of intercept route to match any query params attached
  cy.intercept("POST", `${EAVE_ATOM_INGESTION_ENDPOINT}*`, (req) => {
    // in reality, the ingestion reply doesnt matter, so we'll use this stub
    // to reflect info about the request we want to assert (i.e. data being passed)
    let body = req.body;
    if (typeof(body) === 'string') {
      body = JSON.parse(body);
    }
    req.reply({
      statusCode: 200,
      body,
    });
  }).as(ATOM_INTERCEPTION_EVENT_NAME);
});
