/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave page view atom collection", () => {
  it("fires page view on site load", () => {
    // GIVEN site has Eave script
    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(DUMMY_APP_ROOT);

    // THEN an event is fired
    // Wait for the POST request to be sent
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
    });
  });
});
