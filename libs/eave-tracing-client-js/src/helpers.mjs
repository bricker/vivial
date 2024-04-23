import "./globals.mjs";

/**
 * See https://github.com/matomo-org/matomo/issues/8413
 * To prevent Javascript Error: Uncaught URIError: URI malformed when encoding is not UTF-8. Use this method
 * instead of decodeWrapper if a text could contain any non UTF-8 encoded characters eg
 * a URL like http://apache.matomo/test.html?%F6%E4%FC or a link like
 * <a href="test-with-%F6%E4%FC/story/0">(encoded iso-8859-1 URL)</a>
 */
export function safeDecodeWrapper(url) {
  try {
    return globalThis.eave.decodeWrapper(url);
  } catch (e) {
    return unescape(url);
  }
}

/*
 * Is property defined?
 */
export function isDefined(property) {
  // workaround https://github.com/douglascrockford/JSLint/commit/24f63ada2f9d7ad65afc90e6d949f631935c2480
  var propertyType = typeof property;

  return propertyType !== "undefined";
}

/*
 * Is property a function?
 */
export function isFunction(property) {
  return typeof property === "function";
}

/*
 * Is property an object?
 *
 * @returns {boolean} Returns true if property is null, an Object, or subclass of Object (i.e., an instanceof String, Date, etc.)
 */
export function isObject(property) {
  return typeof property === "object";
}

/*
 * Is property a string?
 */
export function isString(property) {
  return typeof property === "string" || property instanceof String;
}

/*
 * Is property a string?
 */
export function isNumber(property) {
  return typeof property === "number" || property instanceof Number;
}

/*
 * Is property a string?
 */
export function isNumberOrHasLength(property) {
  return (
    isDefined(property) &&
    (isNumber(property) || (isString(property) && property.length))
  );
}

export function isObjectEmpty(property) {
  if (!property) {
    return true;
  }

  var i;
  for (i in property) {
    if (Object.prototype.hasOwnProperty.call(property, i)) {
      return false;
    }
  }

  return true;
}

/**
 * Logs an error in the console.
 *  Note: it does not generate a JavaScript error, so make sure to also generate an error if needed.
 * @param message
 */
export function logConsoleError(message) {
  // needed to write it this way for jslint
  var consoleType = typeof console;
  if (consoleType !== "undefined" && console && console.error) {
    console.error(message);
  }
}

/*
 * apply wrapper
 *
 * @param {Array} parameterArray An array comprising either:
 *      [ 'methodName', optional_parameters ]
 * or:
 *      [ functionObject, optional_parameters ]
 */
export function apply() {
  var i, j, f, parameterArray, trackerCall;

  for (i = 0; i < arguments.length; i += 1) {
    trackerCall = null;
    if (arguments[i] && arguments[i].slice) {
      trackerCall = arguments[i].slice();
    }
    parameterArray = arguments[i];
    f = parameterArray.shift();

    var fParts, context;

    var isStaticPluginCall = isString(f) && f.indexOf("::") > 0;
    if (isStaticPluginCall) {
      // a static method will not be called on a tracker and is not dependent on the existence of a
      // tracker etc
      fParts = f.split("::");
      context = fParts[0];
      f = fParts[1];

      if (
        "object" === typeof globalThis.eave.eave[context] &&
        "function" === typeof globalThis.eave.eave[context][f]
      ) {
        globalThis.eave.eave[context][f].apply(
          globalThis.eave.eave[context],
          parameterArray,
        );
      } else if (trackerCall) {
        // we try to call that method again later as the plugin might not be loaded yet
        // a plugin can call "globalThis.eave.eave.retryMissedPluginCalls();" once it has been loaded and then the
        // method call to "globalThis.eave.eave[context][f]" may be executed
        globalThis.eave.missedPluginTrackerCalls.push(trackerCall);
      }
    } else {
      for (j = 0; j < globalThis.eave.asyncTrackers.length; j++) {
        if (isString(f)) {
          context = globalThis.eave.asyncTrackers[j];

          var isPluginTrackerCall = f.indexOf(".") > 0;

          if (isPluginTrackerCall) {
            fParts = f.split(".");
            if (context && "object" === typeof context[fParts[0]]) {
              context = context[fParts[0]];
              f = fParts[1];
            } else if (trackerCall) {
              // we try to call that method again later as the plugin might not be loaded yet
              globalThis.eave.missedPluginTrackerCalls.push(trackerCall);
              break;
            }
          }

          if (context[f]) {
            context[f].apply(context, parameterArray);
          } else {
            var message =
              "The method '" +
              f +
              '\' was not found in "_paq" variable.  Please have a look at the eave tracker documentation: https://developer.matomo.org/api-reference/tracking-javascript';
            logConsoleError(message);

            if (!isPluginTrackerCall) {
              // do not trigger an error if it is a call to a plugin as the plugin may just not be
              // loaded yet etc
              throw new TypeError(message);
            }
          }

          if (f === "addTracker") {
            // addTracker adds an entry to globalThis.eave.asyncTrackers and would otherwise result in an endless loop
            break;
          }

          if (f === "setTrackerUrl" || f === "setSiteId") {
            // these two methods should be only executed on the first tracker
            break;
          }
        } else {
          f.apply(globalThis.eave.asyncTrackers[j], parameterArray);
        }
      }
    }
  }
}

/*
 * Cross-browser helper function to add event handler
 */
export function addEventListener(element, eventType, eventHandler, useCapture) {
  if (element.addEventListener) {
    element.addEventListener(eventType, eventHandler, useCapture);

    return true;
  }

  if (element.attachEvent) {
    return element.attachEvent("on" + eventType, eventHandler);
  }

  element["on" + eventType] = eventHandler;
}

export function trackCallbackOnLoad(callback) {
  if (globalThis.eave.documentAlias.readyState === "complete") {
    callback();
  } else if (globalThis.eave.windowAlias.addEventListener) {
    globalThis.eave.windowAlias.addEventListener("load", callback, false);
  } else if (globalThis.eave.windowAlias.attachEvent) {
    globalThis.eave.windowAlias.attachEvent("onload", callback);
  }
}

export function trackCallbackOnReady(callback) {
  var loaded = false;

  if (globalThis.eave.documentAlias.attachEvent) {
    loaded = globalThis.eave.documentAlias.readyState === "complete";
  } else {
    loaded = globalThis.eave.documentAlias.readyState !== "loading";
  }

  if (loaded) {
    callback();
    return;
  }

  var _timer;

  if (globalThis.eave.documentAlias.addEventListener) {
    addEventListener(
      globalThis.eave.documentAlias,
      "DOMContentLoaded",
      function ready() {
        globalThis.eave.documentAlias.removeEventListener(
          "DOMContentLoaded",
          ready,
          false,
        );
        if (!loaded) {
          loaded = true;
          callback();
        }
      },
    );
  } else if (globalThis.eave.documentAlias.attachEvent) {
    globalThis.eave.documentAlias.attachEvent(
      "onreadystatechange",
      function ready() {
        if (globalThis.eave.documentAlias.readyState === "complete") {
          globalThis.eave.documentAlias.detachEvent(
            "onreadystatechange",
            ready,
          );
          if (!loaded) {
            loaded = true;
            callback();
          }
        }
      },
    );

    if (
      globalThis.eave.documentAlias.documentElement.doScroll &&
      globalThis.eave.windowAlias === globalThis.eave.windowAlias.top
    ) {
      (function ready() {
        if (!loaded) {
          try {
            globalThis.eave.documentAlias.documentElement.doScroll("left");
          } catch (error) {
            setTimeout(ready, 0);

            return;
          }
          loaded = true;
          callback();
        }
      })();
    }
  }

  // fallback
  addEventListener(
    globalThis.eave.windowAlias,
    "load",
    function () {
      if (!loaded) {
        loaded = true;
        callback();
      }
    },
    false,
  );
}

/*
 * Call plugin hook methods
 */
export function executePluginMethod(methodName, params, callback) {
  if (!methodName) {
    return "";
  }

  var result = "",
    i,
    pluginMethod,
    value,
    isFunction;

  for (i in globalThis.eave.plugins) {
    if (Object.prototype.hasOwnProperty.call(globalThis.eave.plugins, i)) {
      isFunction =
        globalThis.eave.plugins[i] &&
        "function" === typeof globalThis.eave.plugins[i][methodName];

      if (isFunction) {
        pluginMethod = globalThis.eave.plugins[i][methodName];
        value = pluginMethod(params || {}, callback);

        if (value) {
          result += value;
        }
      }
    }
  }

  return result;
}

/*
 * Handle beforeunload event
 *
 * Subject to Safari's "Runaway JavaScript Timer" and
 * Chrome V8 extension that terminates JS that exhibits
 * "slow unload", i.e., calling getTime() > 1000 times
 */
export function beforeUnloadHandler(event) {
  var now;
  globalThis.eave.isPageUnloading = true;

  executePluginMethod("unload");
  now = new Date();
  var aliasTime = now.getTimeAlias();
  if (globalThis.eave.expireDateTime - aliasTime > 3000) {
    globalThis.eave.expireDateTime = aliasTime + 3000;
  }

  /*
   * Delay/pause (blocks UI)
   */
  if (globalThis.eave.expireDateTime) {
    // the things we do for backwards compatibility...
    // in ECMA-262 5th ed., we could simply use:
    //     while (Date.now() < globalThis.eave.expireDateTime) { }
    do {
      now = new Date();
    } while (now.getTimeAlias() < globalThis.eave.expireDateTime);
  }
}

/*
 * Load JavaScript file (asynchronously)
 */
export function loadScript(src, onLoad) {
  var script = globalThis.eave.documentAlias.createElement("script");

  script.type = "text/javascript";
  script.src = src;

  if (script.readyState) {
    script.onreadystatechange = function () {
      var state = this.readyState;

      if (state === "loaded" || state === "complete") {
        script.onreadystatechange = null;
        onLoad();
      }
    };
  } else {
    script.onload = onLoad;
  }

  globalThis.eave.documentAlias
    .getElementsByTagName("head")[0]
    .appendChild(script);
}

/*
 * Get page referrer
 */
export function getReferrer() {
  var referrer = "";

  try {
    referrer = globalThis.eave.windowAlias.top.document.referrer;
  } catch (e) {
    if (globalThis.eave.windowAlias.parent) {
      try {
        referrer = globalThis.eave.windowAlias.parent.document.referrer;
      } catch (e2) {
        referrer = "";
      }
    }
  }

  if (referrer === "") {
    referrer = globalThis.eave.documentAlias.referrer;
  }

  return referrer;
}

/*
 * Extract scheme/protocol from URL
 */
export function getProtocolScheme(url) {
  var e = new RegExp("^([a-z]+):"),
    matches = e.exec(url);

  return matches ? matches[1] : null;
}

/*
 * Extract hostname from URL
 */
export function getHostName(url) {
  // scheme : // [username [: password] @] hostame [: port] [/ [path] [? query] [# fragment]]
  var e = new RegExp("^(?:(?:https?|ftp):)/*(?:[^@]+@)?([^:/#]+)"),
    matches = e.exec(url);

  return matches ? matches[1] : url;
}
export function isPositiveNumberString(str) {
  // !isNaN(str) could be used but does not cover '03' (octal) and '0xA' (hex)
  // nor negative numbers
  return /^[0-9][0-9]*(\.[0-9]+)?$/.test(str);
}
export function filterIn(object, byFunction) {
  var result = {},
    k;
  for (k in object) {
    if (object.hasOwnProperty(k) && byFunction(object[k])) {
      result[k] = object[k];
    }
  }
  return result;
}
export function onlyPositiveIntegers(data) {
  var result = {},
    k;
  for (k in data) {
    if (data.hasOwnProperty(k)) {
      if (isPositiveNumberString(data[k])) {
        result[k] = Math.round(data[k]);
      } else {
        throw new Error(
          'Parameter "' +
            k +
            '" provided value "' +
            data[k] +
            '" is not valid. Please provide a numeric value.',
        );
      }
    }
  }
  return result;
}
export function queryStringify(data) {
  var queryString = "",
    k;
  for (k in data) {
    if (data.hasOwnProperty(k)) {
      queryString +=
        "&" +
        globalThis.eave.encodeWrapper(k) +
        "=" +
        globalThis.eave.encodeWrapper(data[k]);
    }
  }
  return queryString;
}

export function stringStartsWith(str, prefix) {
  str = String(str);
  return str.lastIndexOf(prefix, 0) === 0;
}

export function stringEndsWith(str, suffix) {
  str = String(str);
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

export function stringContains(str, needle) {
  str = String(str);
  return str.indexOf(needle) !== -1;
}

export function removeCharactersFromEndOfString(str, numCharactersToRemove) {
  str = String(str);
  return str.substr(0, str.length - numCharactersToRemove);
}

/**
 * We do not check whether URL contains already url parameter, please use removeUrlParameter() if needed
 * before calling this method.
 * This method makes sure to append URL parameters before a possible hash. Will escape (encode URI component)
 * the set name and value
 */
export function addUrlParameter(url, name, value) {
  url = String(url);

  if (!value) {
    value = "";
  }

  var hashPos = url.indexOf("#");
  var urlLength = url.length;

  if (hashPos === -1) {
    hashPos = urlLength;
  }

  var baseUrl = url.substr(0, hashPos);
  var urlHash = url.substr(hashPos, urlLength - hashPos);

  if (baseUrl.indexOf("?") === -1) {
    baseUrl += "?";
  } else if (!stringEndsWith(baseUrl, "?")) {
    baseUrl += "&";
  }
  // nothing to if ends with ?

  return (
    baseUrl +
    globalThis.eave.encodeWrapper(name) +
    "=" +
    globalThis.eave.encodeWrapper(value) +
    urlHash
  );
}

export function removeUrlParameter(url, name) {
  url = String(url);

  if (
    url.indexOf("?" + name + "=") === -1 &&
    url.indexOf("&" + name + "=") === -1
  ) {
    // nothing to remove, url does not contain this parameter
    return url;
  }

  var searchPos = url.indexOf("?");
  if (searchPos === -1) {
    // nothing to remove, no query parameters
    return url;
  }

  var queryString = url.substr(searchPos + 1);
  var baseUrl = url.substr(0, searchPos);

  if (queryString) {
    var urlHash = "";
    var hashPos = queryString.indexOf("#");
    if (hashPos !== -1) {
      urlHash = queryString.substr(hashPos + 1);
      queryString = queryString.substr(0, hashPos);
    }

    var param;
    var paramsArr = queryString.split("&");
    var i = paramsArr.length - 1;

    for (i; i >= 0; i--) {
      param = paramsArr[i].split("=")[0];
      if (param === name) {
        paramsArr.splice(i, 1);
      }
    }

    var newQueryString = paramsArr.join("&");

    if (newQueryString) {
      baseUrl = baseUrl + "?" + newQueryString;
    }

    if (urlHash) {
      baseUrl += "#" + urlHash;
    }
  }

  return baseUrl;
}

/*
 * Extract parameter from URL
 */
export function getUrlParameter(url, name) {
  var regexSearch = "[\\?&#]" + name + "=([^&#]*)";
  var regex = new RegExp(regexSearch);
  var results = regex.exec(url);
  return results ? safeDecodeWrapper(results[1]) : "";
}

export function trim(text) {
  if (text && String(text) === text) {
    return text.replace(/^\s+|\s+$/g, "");
  }

  return text;
}

/*
 * UTF-8 encoding
 */
export function utf8_encode(argString) {
  return unescape(globalThis.eave.encodeWrapper(argString));
}

/************************************************************
 * sha1
 * - based on sha1 from http://phpjs.org/functions/sha1:512 (MIT / GPL v2)
 ************************************************************/

export function sha1(str) {
  // +   original by: Webtoolkit.info (http://www.webtoolkit.info/)
  // + namespaced by: Michael White (http://getsprink.com)
  // +      input by: Brett Zamir (http://brett-zamir.me)
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   jslinted by: Anthon Pang (https://matomo.org)

  var rotate_left = function (n, s) {
      return (n << s) | (n >>> (32 - s));
    },
    cvt_hex = function (val) {
      var strout = "",
        i,
        v;

      for (i = 7; i >= 0; i--) {
        v = (val >>> (i * 4)) & 0x0f;
        strout += v.toString(16);
      }

      return strout;
    },
    blockstart,
    i,
    j,
    W = [],
    H0 = 0x67452301,
    H1 = 0xefcdab89,
    H2 = 0x98badcfe,
    H3 = 0x10325476,
    H4 = 0xc3d2e1f0,
    A,
    B,
    C,
    D,
    E,
    temp,
    str_len,
    word_array = [];

  str = utf8_encode(str);
  str_len = str.length;

  for (i = 0; i < str_len - 3; i += 4) {
    j =
      (str.charCodeAt(i) << 24) |
      (str.charCodeAt(i + 1) << 16) |
      (str.charCodeAt(i + 2) << 8) |
      str.charCodeAt(i + 3);
    word_array.push(j);
  }

  switch (str_len & 3) {
    case 0:
      i = 0x080000000;
      break;
    case 1:
      i = (str.charCodeAt(str_len - 1) << 24) | 0x0800000;
      break;
    case 2:
      i =
        (str.charCodeAt(str_len - 2) << 24) |
        (str.charCodeAt(str_len - 1) << 16) |
        0x08000;
      break;
    case 3:
      i =
        (str.charCodeAt(str_len - 3) << 24) |
        (str.charCodeAt(str_len - 2) << 16) |
        (str.charCodeAt(str_len - 1) << 8) |
        0x80;
      break;
  }

  word_array.push(i);

  while ((word_array.length & 15) !== 14) {
    word_array.push(0);
  }

  word_array.push(str_len >>> 29);
  word_array.push((str_len << 3) & 0x0ffffffff);

  for (blockstart = 0; blockstart < word_array.length; blockstart += 16) {
    for (i = 0; i < 16; i++) {
      W[i] = word_array[blockstart + i];
    }

    for (i = 16; i <= 79; i++) {
      W[i] = rotate_left(W[i - 3] ^ W[i - 8] ^ W[i - 14] ^ W[i - 16], 1);
    }

    A = H0;
    B = H1;
    C = H2;
    D = H3;
    E = H4;

    for (i = 0; i <= 19; i++) {
      temp =
        (rotate_left(A, 5) + ((B & C) | (~B & D)) + E + W[i] + 0x5a827999) &
        0x0ffffffff;
      E = D;
      D = C;
      C = rotate_left(B, 30);
      B = A;
      A = temp;
    }

    for (i = 20; i <= 39; i++) {
      temp =
        (rotate_left(A, 5) + (B ^ C ^ D) + E + W[i] + 0x6ed9eba1) & 0x0ffffffff;
      E = D;
      D = C;
      C = rotate_left(B, 30);
      B = A;
      A = temp;
    }

    for (i = 40; i <= 59; i++) {
      temp =
        (rotate_left(A, 5) +
          ((B & C) | (B & D) | (C & D)) +
          E +
          W[i] +
          0x8f1bbcdc) &
        0x0ffffffff;
      E = D;
      D = C;
      C = rotate_left(B, 30);
      B = A;
      A = temp;
    }

    for (i = 60; i <= 79; i++) {
      temp =
        (rotate_left(A, 5) + (B ^ C ^ D) + E + W[i] + 0xca62c1d6) & 0x0ffffffff;
      E = D;
      D = C;
      C = rotate_left(B, 30);
      B = A;
      A = temp;
    }

    H0 = (H0 + A) & 0x0ffffffff;
    H1 = (H1 + B) & 0x0ffffffff;
    H2 = (H2 + C) & 0x0ffffffff;
    H3 = (H3 + D) & 0x0ffffffff;
    H4 = (H4 + E) & 0x0ffffffff;
  }

  temp = cvt_hex(H0) + cvt_hex(H1) + cvt_hex(H2) + cvt_hex(H3) + cvt_hex(H4);

  return temp.toLowerCase();
}

/************************************************************
 * end sha1
 ************************************************************/

/*
 * Fix-up URL when page rendered from search engine cache or translated page
 */
export function urlFixup(hostName, href, referrer) {
  if (!hostName) {
    hostName = "";
  }

  if (!href) {
    href = "";
  }

  if (hostName === "translate.googleusercontent.com") {
    // Google
    if (referrer === "") {
      referrer = href;
    }

    href = getUrlParameter(href, "u");
    hostName = getHostName(href);
  } else if (
    hostName === "cc.bingj.com" || // Bing
    hostName === "webcache.googleusercontent.com" || // Google
    hostName.slice(0, 5) === "74.6."
  ) {
    // Yahoo (via Inktomi 74.6.0.0/16)
    href = globalThis.eave.documentAlias.links[0].href;
    hostName = getHostName(href);
  }

  return [hostName, href, referrer];
}

/*
 * Fix-up domain
 */
export function domainFixup(domain) {
  var dl = domain.length;

  // remove trailing '.'
  if (domain.charAt(--dl) === ".") {
    domain = domain.slice(0, dl);
  }

  // remove leading '*'
  if (domain.slice(0, 2) === "*.") {
    domain = domain.slice(1);
  }

  if (domain.indexOf("/") !== -1) {
    domain = domain.substr(0, domain.indexOf("/"));
  }

  return domain;
}

/*
 * Title fixup
 */
export function titleFixup(title) {
  title = title && title.text ? title.text : title;

  if (!isString(title)) {
    var tmp = globalThis.eave.documentAlias.getElementsByTagName("title");

    if (tmp && isDefined(tmp[0])) {
      title = tmp[0].text;
    }
  }

  return title;
}

export function getChildrenFromNode(node) {
  if (!node) {
    return [];
  }

  if (!isDefined(node.children) && isDefined(node.childNodes)) {
    return node.children;
  }

  if (isDefined(node.children)) {
    return node.children;
  }

  return [];
}

export function containsNodeElement(node, containedNode) {
  if (!node || !containedNode) {
    return false;
  }

  if (node.contains) {
    return node.contains(containedNode);
  }

  if (node === containedNode) {
    return true;
  }

  if (node.compareDocumentPosition) {
    return !!(node.compareDocumentPosition(containedNode) & 16);
  }

  return false;
}

// Polyfill for IndexOf for IE6-IE8
export function indexOfArray(theArray, searchElement) {
  if (theArray && theArray.indexOf) {
    return theArray.indexOf(searchElement);
  }

  // 1. Let O be the result of calling ToObject passing
  //    the this value as the argument.
  if (!isDefined(theArray) || theArray === null) {
    return -1;
  }

  if (!theArray.length) {
    return -1;
  }

  var len = theArray.length;

  if (len === 0) {
    return -1;
  }

  var k = 0;

  // 9. Repeat, while k < len
  while (k < len) {
    // a. Let Pk be ToString(k).
    //   This is implicit for LHS operands of the in operator
    // b. Let kPresent be the result of calling the
    //    HasProperty internal method of O with argument Pk.
    //   This step can be combined with c
    // c. If kPresent is true, then
    //    i.  Let elementK be the result of calling the Get
    //        internal method of O with the argument ToString(k).
    //   ii.  Let same be the result of applying the
    //        Strict Equality Comparison Algorithm to
    //        searchElement and elementK.
    //  iii.  If same is true, return k.
    if (theArray[k] === searchElement) {
      return k;
    }
    k++;
  }
  return -1;
}

export function uuidv4() {
  if (isDefined(crypto) && isDefined(crypto.randomUUID)) {
    return crypto.randomUUID();
  }
  // we are in an insecure env or this is an incompatible browser!
  // fallback on some manual uuid jank
  // https://stackoverflow.com/a/2117523/9718199
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) =>
    (
      +c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (+c / 4)))
    ).toString(16),
  );
}

export function getCurrentTimestampInSeconds() {
  return Math.floor(new Date().getTime() / 1000);
}

export function sortObjectsByKeys(value) {
  if (!value || !isObject(value)) {
    return;
  }

  // Object.keys(value) is not supported by all browsers, we get the keys manually
  var keys = [];
  var key;

  for (key in value) {
    if (Object.prototype.hasOwnProperty.call(value, key)) {
      keys.push(key);
    }
  }

  var normalized = {};
  keys.sort();
  var len = keys.length;
  var i;

  for (i = 0; i < len; i++) {
    normalized[keys[i]] = value[keys[i]];
  }

  return normalized;
}

export function generateUniqueId() {
  var id = "";
  var chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  var charLen = chars.length;
  var i;

  for (i = 0; i < 6; i++) {
    id += chars.charAt(Math.floor(Math.random() * charLen));
  }

  return id;
}

export function arrayChunk(theArray, chunkSize) {
  if (!chunkSize || chunkSize >= theArray.length) {
    return [theArray];
  }

  var index = 0;
  var arrLength = theArray.length;
  var chunks = [];

  for (index; index < arrLength; index += chunkSize) {
    chunks.push(theArray.slice(index, index + chunkSize));
  }

  return chunks;
}

export function setExpireDateTime(delay) {
  var now = new Date();
  var time = now.getTime() + delay;

  if (
    !globalThis.eave.expireDateTime ||
    time > globalThis.eave.expireDateTime
  ) {
    globalThis.eave.expireDateTime = time;
  }
}

export function isSameHost(hostName, alias) {
  var offset;

  hostName = String(hostName).toLowerCase();
  alias = String(alias).toLowerCase();

  if (hostName === alias) {
    return true;
  }

  if (alias.slice(0, 1) === ".") {
    if (hostName === alias.slice(1)) {
      return true;
    }

    offset = hostName.length - alias.length;

    if (offset > 0 && hostName.slice(offset) === alias) {
      return true;
    }
  }

  return false;
}

export function isSitePath(path, pathAlias) {
  if (!stringStartsWith(pathAlias, "/")) {
    pathAlias = "/" + pathAlias;
  }

  if (!stringStartsWith(path, "/")) {
    path = "/" + path;
  }

  var matchesAnyPath = pathAlias === "/" || pathAlias === "/*";

  if (matchesAnyPath) {
    return true;
  }

  if (path === pathAlias) {
    return true;
  }

  pathAlias = String(pathAlias).toLowerCase();
  path = String(path).toLowerCase();

  // wildcard path support
  if (stringEndsWith(pathAlias, "*")) {
    // remove the final '*' before comparing
    pathAlias = pathAlias.slice(0, -1);

    // Note: this is almost duplicated from just few lines above
    matchesAnyPath = !pathAlias || pathAlias === "/";

    if (matchesAnyPath) {
      return true;
    }

    if (path === pathAlias) {
      return true;
    }

    // wildcard match
    return path.indexOf(pathAlias) === 0;
  }

  // we need to append slashes so /foobarbaz won't match a site /foobar
  if (!stringEndsWith(path, "/")) {
    path += "/";
  }

  if (!stringEndsWith(pathAlias, "/")) {
    pathAlias += "/";
  }

  return path.indexOf(pathAlias) === 0;
}

/**
 * Convert an object to a query params string
 *
 * @param {object} args
 * @returns {string} query params to attach to a request URL
 */
export function argsToQueryParameters(args) {
  const makeURLSafe = isFunction(globalThis.eave.encodeWrapper)
    ? globalThis.eave.encodeWrapper
    : function (x) {
        return x;
      };
  let qp = "";
  let key;
  for (key of Object.keys(args)) {
    qp += "&" + makeURLSafe(key) + "=" + makeURLSafe(String(args[key]));
  }
  return qp;
}
