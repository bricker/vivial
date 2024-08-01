/* eslint-disable no-unused-expressions */
import { dummyAppRoot } from "../support/constants";

describe("eave UTM and query parameter collection", () => {
  it("includes query params in every atom", () => {
    // GIVEN site has Eave script
    cy.interceptAtomIngestion();

    // WHEN site is initially visited including some query/utm params
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );

    // THEN utm params are included in fired events
    cy.waitForAtom().then((interception) => {
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });
  });

  it("persists the initial query params to include in following atoms", () => {
    cy.interceptAtomIngestion();

    // GIVEN initial visit URL contains query/utm params
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );
    cy.waitForAtom();

    // WHEN performing some other event triggering action
    cy.get("#page-link").click();
    // await btn click
    cy.waitForAtom();

    // THEN query/utm params are still included in the following event
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("statechange");
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });
  });

  it("sends the current page's query params without persisting them", () => {
    cy.interceptAtomIngestion();

    // GIVEN initial visit URL contains query/utm params
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );
    cy.waitForAtom();

    // WHEN navigating to a page w/ different query params
    cy.visit(dummyAppRoot({ path: "/", qp: "search=beans&filter=canned" }));

    // THEN the original saved query/utm params included in the event
    cy.waitForAtom().then((interception) => {
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });

    // WHEN event is triggered after current query params change
    cy.visit(dummyAppRoot({ path: "/", qp: "search=food&approval=fda" }));

    // THEN current query params included in the event, prev qp not included
    cy.waitForAtom().then((interception) => {
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });
  });

  it("overwrites referrer data whenever new utm query parameters are set", () => {
    // GIVEN the utm params get set once
    cy.interceptAtomIngestion();
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );
    cy.waitForAtom().then((interception) => {
      // inital referrer data set
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });

    // WHEN site is visited again with diff utm params
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "gclid=twizzler&utm_campaign=linkedin",
      }),
    );

    // THEN utm params are included in fired events
    cy.waitForAtom().then((interception) => {
      // referrer data not set
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        gclid: "twizzler",
        utm_campaign: "linkedin",
      });
    });
  });

  it("tries to reset traffic src after session expiration", () => {
    cy.interceptAtomIngestion();

    // GIVEN initial visit URL contains query/utm params
    cy.visit(
      dummyAppRoot({
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );
    cy.waitForAtom();

    // WHEN the session expires (and traffic source at the same time)
    cy.expireSessionAndTrafficSourceCookies();

    // THEN eave tries to pull traffic src from curr URL for next event
    cy.get("#page-link").click();
    cy.waitForAtom(); // consume one of click/nav atoms
    cy.waitForAtom().then((interception) => {
      // traffic source brought back from url when available
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });

    // WHEN session expires (and traffic src) and there are no utm params in the current URL
    cy.expireSessionAndTrafficSourceCookies();

    // THEN eave sets a null traffic src
    cy.get("#page-link").click();
    cy.waitForAtom(); // consume one of click/nav atoms
    cy.waitForAtom().then((interception) => {
      // traffic source brought back from url when available
      const traffic_src = JSON.parse(
        interception.response.body.events.browser_event[0].corr_ctx["_eave.traffic_source"],
      );
      expect(traffic_src.tracking_params).to.deep.equal({});
    });
  });
});
