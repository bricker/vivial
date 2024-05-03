/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave form atom collection", () => {
  it("fires atom on form submission", () => {
    cy.interceptAtomIngestion();
    // GIVEN site has a form
    cy.visit(DUMMY_APP_ROOT + "/form");
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN form is submitted
    cy.get("#name").type("Fred");
    cy.get("#email").type("fred@derf.com");
    cy.get("#message").type("hello there");
    cy.get("#formBtn").click();

    // THEN an event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
    });
  });
});
