/* eslint-disable no-unused-expressions */
import { ATOM_INTERCEPTION_EVENT_NAME, dummyAppRoot } from "../support/constants";

describe("eave page view atom collection", () => {
  it("fires page view on site load", () => {
    // GIVEN site has Eave script
    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(dummyAppRoot());

    // THEN an event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("pageload");
    });
  });

  it("fires page view on SPA internal navigation", () => {
    cy.interceptAtomIngestion();

    // GIVEN site is an SPA
    cy.visit(dummyAppRoot());
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN navigating to a subpage/route
    cy.get("#page-link").click();
    // await btn click
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // THEN page view event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("statechange");
    });
  });
});
