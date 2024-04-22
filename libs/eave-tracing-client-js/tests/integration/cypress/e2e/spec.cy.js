/* eslint-disable no-unused-expressions */

describe('eave atom collection', () => {
  it('fires page view on site load', () => {
    // GIVEN site hase Eave script
    // WHEN site is visited
    cy.visit('http://localhost:3300')

    // THEN an event is fired
    cy.interceptAtomIngestion((interception) => {
      expect(interception.response.statusCode).to.equal(200)
    })
  })
})