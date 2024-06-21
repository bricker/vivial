import { ATOM_INTERCEPTION_EVENT_NAME, dummyAppRoot } from "../support/constants";

describe("eave click atom collection", () => {
  it("fires atom on button tag click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a button
    cy.visit(dummyAppRoot());
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
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a external link is clicked
    cy.get("#external-link").click();

    // THEN a link click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.link).to.deep.equal("https://google.com/");
    });
  });

  it("fires link click atoms on internal links", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a internal link
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a raw internal link is clicked
    cy.get("#page-internal-link").click();

    // THEN no atoms are fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.link).to.exist;
      expect(interception.response.body.data.type).to.deep.equal("internal");
    });
  });

  it("fires link click atoms in addition to SPA navigation page views", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a internal link
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a internal SPA navigation link is clicked
    cy.get("#page-link").click();

    // THEN a click event is fired before page view
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.link).to.exist;
      expect(interception.response.body.data.type).to.deep.equal("internal");
    });
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.data.event).to.match(/HistoryChange/);
    });
  });

  it("fires link atom when a external link wraps a button", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a wrapped button
    cy.visit(dummyAppRoot());
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN a button tag inside an anchor tag is clicked
    cy.get("#btn-external-link").click();

    // THEN a link atom is fired, since link click atoms have priority over button click atoms
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response).to.exist;
      expect(interception.response.body.data.link).to.deep.equal("https://google.com/");
    });
  });

  it("fires button click in addition to form submission", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has a form w/ a submit button
    cy.visit(dummyAppRoot({ path: "/form" }));
    // wait for pageview to fire
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN the submit button tag is clicked
    cy.get("#formBtn").click();

    // THEN a button click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.e_n).to.match(/button click/);
    });
  });

  it("fires click event on img tag click", () => {
    cy.interceptAtomIngestion();

    // GIVEN site has an img tag
    cy.visit(dummyAppRoot());
    // wait for page view
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`);

    // WHEN img is clicked
    cy.get("#react-img").click();

    // THEN an image click event is fired
    cy.wait(`@${ATOM_INTERCEPTION_EVENT_NAME}`).then((interception) => {
      expect(interception.response.body.data.e_n).to.match(/img tag clicked/);
      expect(interception.response.body.data.data.src).to.match(/logo.*svg/);
    });
  });
});
