We initialize the clients once and share them because initialization of the clients can be slow. In particular, the Google API clients take around 0.3 seconds to initialize.

Each client is in separate file so that each one is only initialized when it's explicitly imported.
