import { dummyAppRoot } from "../support/constants";

describe("eave click atom collection", () => {
  it("fires atom on button tag click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a button
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.waitForAtom();

    // WHEN a button tag is clicked
    cy.get("#counter-btn").click();

    // THEN a button click event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("BUTTON");
    });
  });

  it("fires atom on external link click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a external
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.waitForAtom();

    // WHEN a external link is clicked
    cy.get("#external-link").click();

    // THEN a link click event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("A");
      expect(interception.response.body.events.browser_event[0].target.attributes.href).to.deep.equal(
        "https://google.com",
      );
    });
  });

  it("fires link click atoms on internal links", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a internal link
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.waitForAtom();

    // WHEN a raw internal link is clicked
    cy.get("#page-internal-link").click();

    // THEN link click atom is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("A");
      expect(interception.response.body.events.browser_event[0].target.attributes.href).to.deep.equal("#");
    });
  });

  it("fires link click atoms in addition to SPA navigation page views", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a internal link
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.waitForAtom();

    // WHEN a internal SPA navigation link is clicked
    cy.get("#page-link").click();

    // THEN a click event is fired before page view
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("A");
      expect(interception.response.body.events.browser_event[0].target.attributes.href).to.deep.equal("/page");
    });
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("PAGE_VIEW");
      expect(interception.response.body.events.browser_event[0].extra.reason).to.deep.equal("statechange");
    });
  });

  // it("fires link atom when a external link wraps a button", () => {
  //   cy.interceptAtomIngestion();

  //   // GIVEN site has a wrapped button
  //   cy.visit(dummyAppRoot());
  //   // wait for pageview to fire
  //   cy.waitForAtom();

  //   // WHEN a button tag inside an anchor tag is clicked
  //   cy.get("#btn-external-link").click();

  //   // THEN a link atom is fired, since link click atoms have priority over button click atoms
  //   cy.waitForAtom().then((interception) => {
  //     expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
  //     expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("A");
  //     expect(interception.response.body.events.browser_event[0].target.attributes.href).to.deep.equal("https://google.com");
  //   });
  // });

  it("fires button click in addition to form submission", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a form w/ a submit button
    cy.visit(dummyAppRoot({ path: "/form" }));
    // wait for pageview to fire
    cy.waitForAtom();

    // WHEN the submit button tag is clicked
    cy.get("#formBtn").click();

    // THEN a button click event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("BUTTON");
    });
  });

  it("fires click event on img tag click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has an img tag
    cy.visit(dummyAppRoot());
    // wait for page view
    cy.waitForAtom();

    // WHEN img is clicked
    cy.get("#react-img").click();

    // THEN an image click event is fired
    cy.waitForAtom().then((interception) => {
      expect(interception.response.body.events.browser_event[0].action).to.deep.equal("CLICK");
      expect(interception.response.body.events.browser_event[0].target.type).to.deep.equal("IMG");
      expect(interception.response.body.events.browser_event[0].target.attributes.src).to.match(/logo.*svg/);
    });
  });
});
