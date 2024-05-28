import { describe, it } from "mocha";
import { ATOM_INTERCEPTION_EVENT_NAME, dummyAppRoot } from "../support/constants";

describe("eave correlation context cookies", () => {
  it("creates ctx and session cookies and attaches cookie data to events", () => {
    // GIVEN site has eave script
    cy.interceptAtomIngestion();

    // WHEN site is visited for the first time w/o visitor/session id
    cy.visit(dummyAppRoot());

    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      // THEN eave generated ctx cookie data is attached to events
      expect(interception.response.body.data._eave_visitor_id).to.exist;
      expect(interception.response.body.data._eave_session_id).to.exist;
    });
  });

  it("makes use of existing ctx and session cookie values", () => {
    // GIVEN site has existing ctx and sesssion cookies set
    const dummyVisitorId = "dummy-vis-uuid";
    const dummySessionId = "dummy-sess-uuid";
    cy.setCookie("_eave_visitor_id", dummyVisitorId);
    cy.setCookie("_eave_session_id", dummySessionId);

    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(dummyAppRoot());

    // THEN page view event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      // THEN eave ctx cookie data is attached to events
      expect(interception.response.body.data._eave_visitor_id).to.equal(dummyVisitorId);
      expect(interception.response.body.data._eave_session_id).to.equal(dummySessionId);
    });
  });
});
