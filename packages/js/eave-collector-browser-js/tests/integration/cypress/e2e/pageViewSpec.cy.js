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
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
    });
  });

  it("fires page view on SPA internal navigation", () => {
    cy.interceptAtomIngestion();

    // GIVEN site is an SPA
    cy.visit(DUMMY_APP_ROOT);
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`)

    // WHEN navigating to a subpage/route
    cy.get("#page-link").click();

    // THEN page view event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.data).to.match(
        /HistoryChange/,
      );
    });
  });
});
