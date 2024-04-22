function interceptAtomIngestion(requestAssertions) {
  // Intercept the POST request
  const interceptionName = 'postRequest'
  cy.intercept('POST', 'https://eave.fyi/api').as(interceptionName)

  // Wait for the POST request to be sent
  cy.wait(`@${interceptionName}`).then(requestAssertions)
}

describe('eave atom collection', () => {
  it('fires page view on site load', () => {
    // GIVEN site hase Eave script
    // WHEN site is visited
    cy.visit('https://example.cypress.io')

    // THEN an event is fired
    interceptAtomIngestion((interception) => {
      expect(interception.request.body).to.exist
      expect(interception.request.method).to.equal('POST')
      expect(interception.response.statusCode).to.equal(200) // Assuming a successful response
    })
  })
})