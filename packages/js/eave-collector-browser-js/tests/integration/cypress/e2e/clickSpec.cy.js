/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave click atom collection", () => {
  it("fires atom on button click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a button
    cy.visit(DUMMY_APP_ROOT);
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a button tag is clicked
    cy.get("#counter-btn").click();

    // THEN a button click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.e_n).to.match(/button click/);
    });
  });

  // TODO: link click
  // link/button is processed 1 time
  // does button click fire on form click?
});
