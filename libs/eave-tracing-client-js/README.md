# Eave Client Tracing

A JS file to include in any web page to collect user actions on the client.

## Notes

This JS code was written to be ES3 compatibile AT MOST to maximize support of old browsers.
So be sure to check browser compatibility of any language features or functions you want to
introduce to the code. Please try to keep the compatibility comment in `eave-client.js`
up to date.

## Dev

run file host server with
```
ruby -run -e httpd -- -p 4000 .
```

run echo server to receive events at w/
```
node echoserv.js 
```

Then nav to [dummy site](http://localhost:4000/bestfileever.html) to test events

## Build

Run `npm run build` to compile the min.js file to `dist/eave-client.min.js`.

We use webpack to bundle all the JS files in `src` together (with `eave-client.js` defined as the
main file in `webpack.config.js`) and consequentially do minification.

Building with development mode on is convenient for debugging in the browser, since it does not
do the minification step. Use production mode in the webpack config to minify the output.
