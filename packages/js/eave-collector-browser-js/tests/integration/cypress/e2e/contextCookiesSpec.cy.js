import { dummyAppRoot } from "../support/constants";

describe("eave correlation context cookies", () => {
  it("creates ctx and session cookies and attaches cookie data to events", () => {
    // GIVEN site has eave script
    cy.interceptAtomIngestion();

    // WHEN site is visited for the first time w/o visitor/session id
    cy.visit(dummyAppRoot());

    cy.waitForAtom().then((interception) => {
      // THEN eave generated ctx cookie data is attached to events
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.visitor_id"]).to.exist;
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.session"]).to.exist;
    });
  });

  it("makes use of existing ctx and session cookie values", () => {
    // GIVEN site has existing visitor_id and sesssion cookies set
    const dummyVisitorId = "dummy-vis-uuid";
    const dummySession = '{"id":"dummy-sess-uuid","start_timestamp":170000}';
    cy.setCookie("_eave.visitor_id", dummyVisitorId);
    cy.setCookie("_eave.session", dummySession);

    cy.interceptAtomIngestion();

    // WHEN site is visited
    cy.visit(dummyAppRoot());

    // THEN page view event is fired
    cy.waitForAtom().then((interception) => {
      // THEN eave ctx cookie data is attached to events
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.visitor_id"]).to.equal(dummyVisitorId);
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.session"]).to.equal(dummySession);
    });
  });

  it("clears account and traffic source cookies on logout link/button click", () => {
    cy.interceptAtomIngestion();

    // GIVEN the user goes to the site with utm params
    cy.visit(dummyAppRoot({ qp: "utm_source=tickletok&utm_campaign=gogole" }));
    cy.waitForAtom();

    // GIVEN the user logs in and eave server sets our account info cookie(s)
    cy.login();
    cy.setCookie("_eave.nc.act.account_id", "encrypted-id");

    // THEN acccount and traffic src cookies should exist on events
    cy.get("#counter-btn").click();
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.nc.act.account_id"]).to.equal(
        "encrypted-id",
      );

      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });

    // WHEN the user logs out
    cy.get("#logout").click();
    cy.waitForAtom(); // consume click
    cy.waitForAtom(); // consume nav to logout page

    // THEN the eave account and traffic src cookies are cleared/reset
    cy.get("#page-link").click();
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.nc.act.account_id"]).to.not.exist;

      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({});
    });
  });

  it("clears account and traffic source cookies on logout link/button child-element click", () => {
    cy.interceptAtomIngestion();

    // GIVEN the user goes to the site with utm params
    cy.visit(dummyAppRoot({ qp: "utm_source=tickletok&utm_campaign=gogole" }));
    cy.waitForAtom();

    // GIVEN the user logs in and eave server sets our account info cookie(s)
    cy.login();
    cy.setCookie("_eave.nc.act.account_id", "encrypted-id");

    // THEN acccount and traffic src cookies should exist on events
    cy.get("#counter-btn").click();
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.nc.act.account_id"]).to.equal(
        "encrypted-id",
      );

      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });

    // WHEN the user clicks a sub-element of the logout button
    cy.get("#sign-out-svg").click();
    cy.waitForAtom(); // consume click
    cy.waitForAtom(); // consume nav to logout page

    // THEN the eave account and traffic src cookies are cleared/reset
    cy.get("#page-link").click();
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].corr_ctx["_eave.nc.act.account_id"]).to.not.exist;

      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({});
    });
  });
});
