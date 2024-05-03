/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave form atom collection", () => {
  it("fires atom on form submission", () => {
    // GIVEN site has a form
    cy.visit(DUMMY_APP_ROOT + "/form");

    // WHEN form is submitted
    cy.interceptAtomIngestion();
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
