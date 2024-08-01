/* eslint-disable no-unused-expressions */
import { dummyAppRoot } from "../support/constants";

describe("eave form atom collection", () => {
  it("fires atom on form submission", () => {
    cy.interceptAtomIngestion();
    // GIVEN site has a form
    cy.visit(dummyAppRoot({ path: "/form" }));
    cy.waitForAtom();

    // WHEN form is submitted
    cy.get("#name").type("Fred");
    // wait for input click event
    cy.waitForAtom();

    cy.get("#email").type("fred@derf.com");
    // wait for input click event
    cy.waitForAtom();

    cy.get("#message").type("hello there");
    // wait for input click event
    cy.waitForAtom();

    cy.get("#formBtn").click();
    // wait for button click event
    cy.waitForAtom();

    // THEN an event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("FORM_SUBMISSION");
    });
  });
});
