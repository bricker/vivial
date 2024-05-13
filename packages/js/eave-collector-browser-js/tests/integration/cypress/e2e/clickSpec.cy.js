/* eslint-disable no-unused-expressions */
import {
  ATOM_INTERCEPTION_EVENT_NAME,
  DUMMY_APP_ROOT,
} from "../support/constants";

describe("eave click atom collection", () => {
  it("fires atom on button tag click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a button
    cy.visit(DUMMY_APP_ROOT);
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a button tag is clicked
    cy.get("#counter-btn").click();

    // THEN a button click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.e_n).to.match(/button click/);
    });
  });

  it("fires atom on external link click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a external
    cy.visit(DUMMY_APP_ROOT);
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a external link is clicked
    cy.get("#external-link").click();

    // THEN a link click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.link).to.deep.equal(
        "https://google.com/",
      );
    });
  });

  it("doesn't fire link click atoms on internal links", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a internal link
    cy.visit(DUMMY_APP_ROOT);
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a raw internal link is clicked
    cy.get("#page-internal-link").click();

    // THEN no atoms are fired
    // (symbolized by not needing to wait and consume an atom before the next one)

    // WHEN a internal SPA navigation link is clicked
    cy.get("#page-link").click();

    // THEN only the navigation event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.data.event).to.match(/HistoryChange/);
    });
  });

  // NOTE: test failing bcus wrapping link is identified as the primary, but then
  //       the link ends up being internal, so no atom is fired despite click event
  //       being consumed by the handler.
  // it("fires button atom when a internal link wraps a button", () => {
  //   cy.interceptAtomIngestion();

  //   // GIVEN site has a wrapped button
  //   cy.visit(DUMMY_APP_ROOT);
  //   // wait for pageview to fire
  //   cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

  //   // WHEN a button tag inside an anchor tag is clicked
  //   cy.get("#btn-internal-link").click();

  //   // THEN a button click atom is fired, since internal links are not logged
  //   cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
  //     expect(interception.response).to.exist;
  //     expect(interception.response.body.data.e_n).to.match(/button click/);
  //   });
  // });

  it("fires link atom when a external link wraps a button", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a wrapped button
    cy.visit(DUMMY_APP_ROOT);
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a button tag inside an anchor tag is clicked
    cy.get("#btn-external-link").click();

    // THEN a link atom is fired, since link click atoms have priority over button click atoms
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.link).to.deep.equal(
        "https://google.com/",
      );
    });
  });

  it("fires button click in addition to form submission", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a form w/ a submit button
    cy.visit(DUMMY_APP_ROOT + "/form");
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN the submit button tag is clicked
    cy.get("#formBtn").click();

    // THEN a button click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.e_n).to.match(/button click/);
    });
  });
});
