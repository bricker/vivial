/* eslint-disable no-unused-expressions */
function interceptAtomIngestion(requestAssertions) {
  // Intercept the ingestion request and mock resp
  const interceptionName = 'atomFired'
  cy.intercept('POST', 'http://localhost:3000/matomo*', (req) => {
    req.reply({
      statusCode: 200,
      body: {},
    })
  }).as(interceptionName)

  // Wait for the POST request to be sent
  cy.wait(`@${interceptionName}`).then(requestAssertions)
}

describe('eave atom collection', () => {
  it('fires page view on site load', () => {
    // GIVEN site hase Eave script
    // WHEN site is visited
    cy.visit('http://localhost:3300')

    // THEN an event is fired
    interceptAtomIngestion((interception) => {
      expect(interception.request.body).to.exist
      expect(interception.request.method).to.equal('POST')
      expect(interception.response.statusCode).to.equal(200) // Assuming a successful response
    })
  })
})