/* eslint-disable no-unused-expressions */
import { describe, expect, it } from "mocha";
import { ATOM_INTERCEPTION_EVENT_NAME, dummyAppRoot } from "../support/constants";

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
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      // current page
      expect(interception.response.body.data.queryParams).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
      // saved referrer storage
      expect(interception.response.body.data._eave_referrer_query_params).to.deep.equal({
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
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN performing some other event triggering action
    cy.get("#page-link").click();
    // await btn click
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // THEN query/utm params are still included in the following event
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.data.event).to.match(/HistoryChange/);
      expect(interception.response.body.data._eave_referrer_query_params).to.deep.equal({
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
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN navigating to a page w/ different query params
    cy.visit(dummyAppRoot({ path: "/", qp: "search=beans&filter=canned" }));

    // THEN current query params AND initial saved query/utm params included in the event
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data._eave_referrer_query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
      expect(interception.response.body.data.queryParams).to.deep.equal({
        search: "beans",
        filter: "canned",
      });
    });

    // WHEN event is triggered after current query params change
    cy.visit(dummyAppRoot({ path: "/", qp: "search=food&approval=fda" }));

    // THEN current query params included in the event, prev qp not included
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data._eave_referrer_query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
      expect(interception.response.body.data.queryParams).to.deep.equal({
        search: "food",
        approval: "fda",
      });
    });
  });

  it("doesnt set referrer data if there is an existing session", () => {
    // GIVEN there is an existing session cookie
    cy.setCookie("_eave_session_id", "session");
    cy.interceptAtomIngestion();

    // WHEN site is initially visited including some query/utm params
    cy.visit(
      dummyAppRoot({
        path: "/page",
        qp: "utm_source=tickletok&utm_campaign=gogole",
      }),
    );

    // THEN utm params are included in fired events
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      // current page qp still set
      expect(interception.response.body.data.queryParams).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
      // referrer data not set
      expect(interception.response.body.data._eave_referrer_query_params).to.not.exist;
    });
  });
});
