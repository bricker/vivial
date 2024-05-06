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

import {
  ATOM_INGESTION_ROUTE,
  ATOM_INTERCEPTION_EVENT_NAME,
  EAVE_API_ROOT,
} from "./constants";

/**
 * This intercept helper MUST be called before the atoms we want to intercept are fired,
 * including the pageView ones fired on cy.visit.
 */
Cypress.Commands.add("interceptAtomIngestion", () => {
  // Intercept the ingestion request and mock resp.
  // wildcard at end of intercept route to match any query params attached
  cy.intercept("POST", `${EAVE_API_ROOT}${ATOM_INGESTION_ROUTE}*`, (req) => {
    // in reality, the ingestion reply doesnt matter, so we'll use this stub
    // to reflect info about the request we want to assert (i.e. data being passed)
    const qp = new URL(req.url).searchParams;
    const data = {};
    for (const [key, val] of qp) {
      data[key] = decodeURIComponent(val);
    }
    req.reply({
      statusCode: 200,
      body: {
        data,
      },
    });
  }).as(ATOM_INTERCEPTION_EVENT_NAME);
});

/**
 * Make sure a timeout occurs.
 * Useful for testing that no further atoms are fired after an action.
 *
 * @example cy.wait(5000).waitForTimeout(6000); // 6s
 */
Cypress.Commands.add('waitForTimeout', { prevSubject: true }, (subject, timeout) => {
  return new Cypress.Promise(resolve => {
    // Chain a should() assertion with an assertion that will always fail
    // This will trigger Cypress to retry the command until the timeout
    // Without failing the test
    cy.wrap(subject, { timeout }).should(() => {
      // Log a message indicating the timeout
      Cypress.log({
        name: 'Timeout',
        message: [`Waited for ${timeout}ms without failing the test`],
        consoleProps: () => {
          return {
            Timeout: timeout
          };
        }
      });
      // Resolve the promise to continue the test without failing
      resolve(subject);
    });
  });
});
