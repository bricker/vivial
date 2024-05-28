# Eave Client Tracing

Include the JS client via snippet/script tag to track user interactions with a webpage,
sending data to the Eave backend for further processing and organization.

Eave browser client manages its own visitor ID and session ID tracking so you don't have to!

Project builds to `collector.js` file that can be included in any web page to collect user actions in the browser.

Forked from the BSD-3/GPLv3 licensed [Matomo piwik.js file](https://github.com/matomo-org/matomo/blob/5.x-dev/js/piwik.js).

## Notes

The original Matomo JS code was written to be ES3 compatibile AT MOST to maximize support of old browsers.
Webpack+Babel is currently configured to transpile all code to ES5 for browser compatibility, so it should be
possible to make use of ES6 features if you like.

## Dev

Requires Node.js and NPM.

Run the `./bin/setup` script to install dev dependencies and get started. Refrain from adding any
direct NPM dependencies to the client code under `src/`, as it is intended to be run in the browser.
(webpack is technically capable of building node_modules with our browser JS code, but we should avoid
that unless absolutely necessary.)

### Secure context

Some features require a secure context (https). For example, `crypto.randomUUID` only works in secure contexts. Additionally, all cookies managed by Eave have the `Secure` flag enabled, which restricts cookie access to secure contexts only.

On a production website, HTTPS is mandatory for Eave to function properly. We do not support non-HTTPS contexts in production environments.

During local development, it can be more problematic because your local development server may not be serving traffic over HTTPS.

There are a few ways to deal with this:

1. If you're connecting to your local server via the `localhost` hostname, then everything will probably work out of the box. This is because the [`Set-Cookie` specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#secure) explicitly allows `localhost` to use features restricted to secure contexts, even when serving over an unencrypted connection. So `Secure` cookies, `crypto.randomUUID()` etc. will work when the hostname is `localhost`. The `localhost` "TLD" is also supported (eg `yourapp.localhost` will work).

2. If you're connecting to your local server through another TLD (not `localhost`), HTTPS is required. This will probably involve creating and installing a self-signed certificate.

### Testing

Unit tests for code that isn't browser dependent can be found in `tests/unit/` and run via `npm test`/`npm run unit-test`.

End-to-End tests for code that does require browser features (or general e2e pipeline testing) can be found in
`tests/integration/cypress/e2e/`, along with accompanying React dummy app in which we embed the eave-client.min.js.
End-to-End tests can be run via `npm run e2e-test`.

### Build

Run `npm run build` to compile the min.js file to `dist/collector.js`. The `webpack.config.js`
file sets the default compilation mode to development for easier local debugging. To make a prod
build, run `npm run build -- --mode production`.

We use webpack to bundle all the JS files in `src` together (with `main.ts` defined as the
main file in `webpack.config.js`) and consequentially do minification.

Building with development mode on is convenient for debugging in the browser, since it does not
do the minification step. Use production mode via CLI or in webpack config to minify the output.
