# Eave Client Tracing

Include the JS client via snippet/script tag to track user interactions with a webpage,
sending data to the Eave backend for further processing and organization.

Eave browser client manages its own visitor ID and session ID tracking so you don't have to!

Project builds to `eave-client.min.js` file that can be included in any web page to collect user actions in the browser.

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

JS files under `src/` currently requried to use the `.mjs` extension to make ES6 imports work for unit tests.

### Adding new tracking events

You'll need to add a new member function to the Tracker "class" in `tracker.js` that
calls the `logEvent()` function (or one of the other `log*` functions defined in it) on some action.
You'll probably want to add some private globals to Tracker as well to ensure adding
the event listeners is idempotent.

e.g.

```js
this.enableButtonClickTracking = function (enable) {
  if (buttonClickTrackingEnabled) {
    return;
  }
  buttonClickTrackingEnabled = true;

  if (!clickListenerInstalled) {
    clickListenerInstalled = true;
    h.trackCallbackOnReady(function () {
      var element = global.ev.documentAlias.body;
      addClickListener(element, enable, true);
    });
  }
};
```

Then push the name of the function you created onto the `_paq` list in `globals.js`
to apply your new tracking function it when the script is loaded in the browser.

```js
_paq.push(["name of your function"])
```

### Testing

Unit tests for code that isn't browser dependent can be found in `tests/unit/` and run via `npm test`/`npm run unit-test`.

End-to-End tests for code that does require browser features (or general e2e pipeline testing) can be found in
`tests/integration/cypress/e2e/`, along with accompanying React dummy app in which we embed the eave-client.min.js.
End-to-End tests can be run via `npm run e2e-test`.

### Build

Run `npm run build` to compile the min.js file to `dist/eave-client.min.js`. The `webpack.config.js`
file sets the default compilation mode to development for easier local debugging. To make a prod
build, run `npm run build -- --mode production`.

We use webpack to bundle all the JS files in `src` together (with `eave-client.js` defined as the
main file in `webpack.config.js`) and consequentially do minification.

Building with development mode on is convenient for debugging in the browser, since it does not
do the minification step. Use production mode via CLI or in webpack config to minify the output.
