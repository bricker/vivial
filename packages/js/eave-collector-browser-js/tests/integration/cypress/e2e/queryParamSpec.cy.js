/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave UTM and query parameter collection", () => {
  it("includes query params in page view atom", () => {
    // GIVEN site has Eave script
    cy.interceptAtomIngestion();

    // WHEN site is initially visited including some query/utm params
    cy.visit(`${DUMMY_APP_ROOT}/page?utm_source=tickletok&utm_campaign=gogole`);

    // THEN utm params are included in fired events
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });
  });

  it("persists the initial query params to include in following atoms", () => {
    cy.interceptAtomIngestion();

    // GIVEN initial visit URL contains query/utm params
    cy.visit(`${DUMMY_APP_ROOT}/page?utm_source=tickletok&utm_campaign=gogole`);
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN performing some other event triggering action
    cy.get("#page-link").click();

    // THEN query/utm params are still included in the following event
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.data).to.match(/HistoryChange/);
      expect(interception.response.body.data.query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
      });
    });
  });

  it("sends the current page's query params without persisting them", () => {
    cy.interceptAtomIngestion();

    // GIVEN initial visit URL contains query/utm params
    cy.visit(`${DUMMY_APP_ROOT}/page?utm_source=tickletok&utm_campaign=gogole`);
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN navigating to a page w/ different query params
    cy.visit(`${DUMMY_APP_ROOT}/?search=beans&filter=canned`);

    // THEN current query params AND initial saved query/utm params included in the event
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
        search: "beans",
        filter: "canned",
      });
    });

    // WHEN event is triggered after current query params change
    cy.visit(`${DUMMY_APP_ROOT}/?search=food&approval=fda`);

    // THEN current query params included in the event, prev qp not included
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.query_params).to.deep.equal({
        utm_source: "tickletok",
        utm_campaign: "gogole",
        search: "food",
        approval: "fda",
      });
    });
  });
});
