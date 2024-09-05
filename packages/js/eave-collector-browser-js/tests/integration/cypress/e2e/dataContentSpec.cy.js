import { dummyAppRoot } from "../support/constants";

describe("atom content", () => {
  // NOTE: this test wont run itself in a different browser; you'll have
  // to manually run the cypress tests in a different browser env
  it("device fields populated in non-chromium browsers", () => {
    // GIVEN browser is not chromium based (to test
    // client hints API for expansion, or UAParser.js fallback)
    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(dummyAppRoot());

    // THEN an event is fired containing device info
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].device.user_agent).to.exist;
      expect(interception.response.body.events.browser_event[0].device.brands).to.have.length.greaterThan(0);
      expect(interception.response.body.events.browser_event[0].device.platform).to.exist;
      expect(interception.response.body.events.browser_event[0].device.mobile).to.exist;
      expect(interception.response.body.events.browser_event[0].device.platform_version).to.exist;
    });
  });
});
