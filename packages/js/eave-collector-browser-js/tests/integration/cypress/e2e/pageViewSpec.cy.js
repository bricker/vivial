/* eslint-disable no-unused-expressions */
import { dummyAppRoot } from "../support/constants";

describe("eave page view atom collection", () => {
  it("fires page view on site load", () => {
    // GIVEN site has Eave script
    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(dummyAppRoot());

    // THEN an event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("pageload");
    });
  });

  it("fires page view on SPA internal navigation", () => {
    cy.interceptAtomIngestion();

    // GIVEN site is an SPA
    cy.visit(dummyAppRoot());
    cy.waitForAtom();

    // WHEN navigating to a subpage/route
    cy.get("#page-link").click();
    // await btn click
    cy.waitForAtom();

    // THEN page view event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("statechange");
    });
  });
});
