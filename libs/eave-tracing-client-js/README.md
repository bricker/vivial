# Eave Client Tracing

A JS file to include in any web page to collect user actions on the client.

## Notes

This JS code is designed to be ES3 compatibile AT MOST to maximize support of old browsers. It also depends heavily
on the weird scope properties of `var` to work, so updating to use ES6 `let`/`const` is not straightforward.

## Dev

run file host server with
```
ruby -run -e httpd -- -p 4000 .
```

run echo server w/ 
```
node echoserv.js 
```

Then nav to [dummy site](http://localhost:4000/bestfileever.html) to test events
