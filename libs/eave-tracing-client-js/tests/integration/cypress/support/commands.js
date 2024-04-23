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

import { ATOM_INGESTION_ROUTE, EAVE_API_ROOT } from "./constants";

Cypress.Commands.add("interceptAtomIngestion", (requestAssertions) => {
  // Intercept the ingestion request and mock resp
  const interceptionName = "atomFired";
  // wildcard at end of intercept route to match any query params attached
  cy.intercept("POST", `${EAVE_API_ROOT}${ATOM_INGESTION_ROUTE}*`, (req) => {
    // in reality, the ingestion reply doesnt matter, so we'll use this stub
    // to reflect info about the request we want to assert (i.e. data being passed)
    const qp = new URL(req.url).searchParams;
    console.log(Object.fromEntries(qp.entries()))
    req.reply({
      statusCode: 200,
      body: {
        data: Object.fromEntries(qp.entries()),
      },
    });
  }).as(interceptionName);

  // Wait for the POST request to be sent
  cy.wait(`@${interceptionName}`).then(requestAssertions);
});
