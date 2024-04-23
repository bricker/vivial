/* eslint-disable no-unused-expressions */
import { DUMMY_APP_ROOT } from "../support/constants";

// TODO: cookies not working when run headless from cli
describe("eave atom collection", () => {
  it("fires page view on site load", () => {
    // GIVEN site hase Eave script
    // WHEN site is visited
    cy.visit(DUMMY_APP_ROOT);

    // THEN an event is fired
    cy.interceptAtomIngestion((interception) => {
      expect(interception.response).to.exist;
    });
  });

  it("creates ctx and session cookies and attaches cookie data to events", () => {
    // GIVEN site has eave script
    // WHEN site is visited
    cy.visit(DUMMY_APP_ROOT);

    // THEN page view event is fired
    cy.interceptAtomIngestion((interception) => {
      expect(interception.response.body).to.exist;
      // THEN eave generated ctx cookie data is attached to events
      expect(interception.response.body.data.visitor_id).to.exist;
      expect(interception.response.body.data.session_id).to.exist;
    });
  });

  it("makes use of existing ctx and session cookie values", () => {
    // GIVEN site has existing ctx and sesssion cookies set
    const dummyVisitorId = "dummy-vis-uuid"
    const dummySessionId = "dummy-sess-uuid"
    cy.setCookie(
      "eave.context",
      JSON.stringify({
        visitor_id: dummyVisitorId,
      }),
    );
    cy.setCookie("eave.session", dummySessionId);

    // WHEN site is visited
    cy.visit(DUMMY_APP_ROOT);

    // THEN page view event is fired
    cy.interceptAtomIngestion((interception) => {
      expect(interception.response.body).to.exist;
      // THEN eave ctx cookie data is attached to events
      expect(interception.response.body.data.visitor_id).to.equal(dummyVisitorId);
      expect(interception.response.body.data.session_id).to.equal(dummySessionId);
    });
  });
});
