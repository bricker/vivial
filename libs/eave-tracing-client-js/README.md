# Eave Client Tracing

A JS file to include in any web page to collect user actions on the client.
Forked from the BSD-3/GPLv3 licensed [Matomo piwik.js file](https://github.com/matomo-org/matomo/blob/5.x-dev/js/piwik.js).

## Notes

The original Matomo JS code was written to be ES3 compatibile AT MOST to maximize support of old browsers.
Webpack+Babel is currently configured to transpile all code to ES5 for browser compatibility, so it should be
possible to make use of ES6 features if you like.

## Dev

run file host server with
```
ruby -run -e httpd -- -p 4000 .
```

run echo server to receive events at w/
```
node echoserv.js 
```

Then nav to [dummy site](http://localhost:4000/testing.html) to test events

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

## Build

Run `npm run build` to compile the min.js file to `dist/eave-client.min.js`. The `webpack.config.js`
file sets the default compilation mode to development for easier local debugging. To make a prod
build, run `npm run build -- --mode production`.

We use webpack to bundle all the JS files in `src` together (with `eave-client.js` defined as the
main file in `webpack.config.js`) and consequentially do minification.

Building with development mode on is convenient for debugging in the browser, since it does not
do the minification step. Use production mode via CLI or in webpack config to minify the output.
