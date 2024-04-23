/* eslint-disable no-unused-expressions */
import { DUMMY_APP_ROOT } from "../support/constants";

describe('eave atom collection', () => {
  it('fires page view on site load', () => {
    // GIVEN site hase Eave script
    // WHEN site is visited
    cy.visit(DUMMY_APP_ROOT)

    // THEN an event is fired
    cy.interceptAtomIngestion((interception) => {
      expect(interception.response.statusCode).to.equal(200)
    })
  })
})