/* eslint-disable no-unused-expressions */
import { ATOM_INTERCEPTION_EVENT_NAME, dummyAppRoot } from "../support/constants";

describe("eave form atom collection", () => {
  it("fires atom on form submission", () => {
    cy.interceptAtomIngestion();
    // GIVEN site has a form
    cy.visit(dummyAppRoot({ path: "/form" }));
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN form is submitted
    cy.get("#name").type("Fred");
    cy.get("#email").type("fred@derf.com");
    cy.get("#message").type("hello there");
    cy.get("#formBtn").click();
    // wait for button click event
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // THEN an event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.data.event).to.match(/FormSubmit/);
    });
  });
});
