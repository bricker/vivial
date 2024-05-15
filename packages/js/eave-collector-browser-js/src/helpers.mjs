// @ts-check

import "./globals.mjs";
// eslint-disable-next-line no-unused-vars
import * as Types from "./types.js";

/** @type {Types.GlobalEaveWindow} */
// @ts-ignore
const eaveWindow = window;

/**
 * See https://github.com/matomo-org/matomo/issues/8413
 * To prevent Javascript Error: Uncaught URIError: URI malformed when encoding is not UTF-8. Use this method
 * instead of decodeWrapper if a text could contain any non UTF-8 encoded characters eg
 * a URL like http://apache.matomo/test.html?%F6%E4%FC or a link like
 * <a href="test-with-%F6%E4%FC/story/0">(encoded iso-8859-1 URL)</a>
 */

/**
 * Safely decodes a URI component. If decoding using `decodeURIComponent` fails,
 * it falls back to `unescape`.
 *
 * See https://github.com/matomo-org/matomo/issues/8413
 * To prevent Javascript Error: Uncaught URIError: URI malformed when encoding is not UTF-8. Use this method
 * instead of decodeWrapper if a text could contain any non UTF-8 encoded characters eg
 * a URL like http://apache.matomo/test.html?%F6%E4%FC or a link like
 * <a href="test-with-%F6%E4%FC/story/0">(encoded iso-8859-1 URL)</a>
 *
 * @param {string} url - The URL or URI component to decode.
 * @returns {string} Returns the decoded URL or URI component.
 */
export function safeDecodeWrapper(url) {
  try {
    return decodeURIComponent(url);
  } catch (e) {
    return unescape(url);
  }
}

/**
 * Checks if a property is defined.
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is defined, false otherwise.
 */
export function isDefined(property) {
  // workaround https://github.com/douglascrockford/JSLint/commit/24f63ada2f9d7ad65afc90e6d949f631935c2480
  const propertyType = typeof property;
  return propertyType !== "undefined";
}

/**
 * Checks if a property is a function.
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is a function, false otherwise.
 */
export function isFunction(property) {
  return typeof property === "function";
}

/**
 * Checks if a property is an object.
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is an object, false otherwise.
 */
export function isObject(property) {
  return typeof property === "object";
}

/**
 * Checks if a property is a string.
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is a string, false otherwise.
 */
export function isString(property) {
  return typeof property === "string" || property instanceof String;
}

/**
 * Checks if a property is a number.
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is a number, false otherwise.
 */
export function isNumber(property) {
  return typeof property === "number" || property instanceof Number;
}

/**
 * Checks if a property is a number or has a length (in the case of strings or arrays).
 * @param {any} property - The property to check.
 * @returns {boolean} Returns true if the property is a number or has a length, false otherwise.
 */
export function isNumberOrHasLength(property) {
  return (
    isDefined(property) &&
    (isNumber(property) || (isString(property) && property.length))
  );
}

/**
 * Checks if an object is empty.
 * @param {Object} property - The object to check.
 * @returns {boolean} Returns true if the object is empty, false otherwise.
 */
export function isObjectEmpty(property) {
  if (!property) {
    return true;
  }

  return Object.keys(property).length === 0;
}


/**
 * Logs an error message to the console.
 * Note: It does not generate a JavaScript error.
 * @param {string} message - The error message to log.
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
              '\' was not found in "settings" variable.  Please have a look at the eave tracker documentation: https://developer.matomo.org/api-reference/tracking-javascript';
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

/**
 * @param {() => void} callback
 *
 * @noreturn
 */
export function trackCallbackOnLoad(callback) {
  if (document.readyState === "complete") {
    callback();
  } else {
    window.addEventListener("load", callback, false);
  }
}

/**
 * @param {() => void} callback
 *
 * @noreturn
 */
export function trackCallbackOnReady(callback) {
  let loaded = document.readyState !== "loading";

  if (loaded) {
    callback();
    return;
  }

  document.addEventListener(
    "DOMContentLoaded",
    function ready() {
      document.removeEventListener(
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

  // fallback
  window.addEventListener(
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

/**
 * Call plugin hook methods
 *
 * @param {string} methodName
 * @param {object} [params]
 * @param {(hookName: string, userHook: object | string) => object | null} [callback]
 *
 * @returns {string}
 */
export function executePluginMethod(methodName, params, callback) {
  if (!methodName) {
    return "";
  }

  let result = "";
  let pluginMethod;
  let value;
  let isFunction;

  for (const i of Object.keys(globalThis.eave.plugins)) {
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

  return result;
}

/**
 * Handle beforeunload event
 *
 * Subject to Safari's "Runaway JavaScript Timer" and
 * Chrome V8 extension that terminates JS that exhibits
 * "slow unload", i.e., calling getTime() > 1000 times
 *
 * @param {Event} _event
 */
export function beforeUnloadHandler(_event) {
  globalThis.eave.isPageUnloading = true;

  executePluginMethod("unload");
  let now = new Date();
  const time = now.getTime();

  if (globalThis.eave.expireDateTime - time > 3000) {
    globalThis.eave.expireDateTime = time + 3000;
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
    } while (now.getTime() < globalThis.eave.expireDateTime);
  }
}

/**
 * Load JavaScript file (asynchronously)
 *
 * @param {string} src
 * @param {() => void} onLoad
 *
 * @noreturn
 */
export function loadScript(src, onLoad) {
  const script = document.createElement("script");

  script.type = "text/javascript";
  script.src = src;
  script.onload = onLoad;

  document
    .getElementsByTagName("head")[0]
    .appendChild(script);
}

/**
 * Get page referrer
 *
 * @returns {string}
 */
export function getReferrer() {
  let /** @type {string | null | undefined} */ referrer = "";

  try {
    referrer = window.top?.document.referrer;
  } catch (e) {
    if (window.parent) {
      try {
        referrer = window.parent.document.referrer;
      } catch (e2) {
        referrer = "";
      }
    }
  }

  if (!referrer) {
    referrer = document.referrer;
  }

  return referrer;
}

/**
 * Extract scheme/protocol from URL
 *
 * @param {string} url
 *
 * @returns {string | null}
 */
export function getProtocolScheme(url) {
  const e = new RegExp("^([a-z]+):");
  const matches = e.exec(url);

  return matches ? matches[1] : null;
}

/**
 * Extract hostname from URL
 *
 * @param {string} url
 *
 * @returns {string} The hostname if found, otherwise the unmodified input
 */
export function getHostName(url) {
  // scheme : // [username [: password] @] hostame [: port] [/ [path] [? query] [# fragment]]
  const e = new RegExp("^(?:(?:https?|ftp):)/*(?:[^@]+@)?([^:/#]+)");
  const matches = e.exec(url);

  return matches ? matches[1] : url;
}

/**
 * @param {string} str
 *
 * @returns {boolean}
 */
export function isPositiveNumberString(str) {
  // !isNaN(str) could be used but does not cover '03' (octal) and '0xA' (hex)
  // nor negative numbers
  return /^[0-9][0-9]*(\.[0-9]+)?$/.test(str);
}

/**
 * @param {object} object
 * @param {(object: object) => boolean} byFunction
 *
 * @returns {object}
 */
export function filterIn(object, byFunction) {
  const result = {};

  for (const k of Object.keys(object)) {
    if (byFunction(object[k])) {
      result[k] = object[k];
    }
  }
  return result;
}

/**
 * @param {object} data
 *
 * @returns {object}
 */
export function onlyPositiveIntegers(data) {
  const result = {};

  for (const k of Object.keys(data)) {
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

  return result;
}

/**
 * @param {object} data
 *
 * @returns {string}
 */
export function queryStringify(data) {
  let queryString = "";

  for (const k of Object.keys(data)) {
    queryString +=
      "&" +
      encodeURIComponent(k) +
      "=" +
      encodeURIComponent(data[k]);
  }
  return queryString;
}

/**
 * @param {string} str
 * @param {string} prefix
 *
 * @returns {boolean}
 */
export function stringStartsWith(str, prefix) {
  str = String(str);
  return str.lastIndexOf(prefix, 0) === 0;
}

/**
 * @param {string} str
 * @param {string} suffix
 *
 * @returns {boolean}
 */
export function stringEndsWith(str, suffix) {
  str = String(str);
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

/**
 * @param {string} str
 * @param {string} needle
 *
 * @returns {boolean}
 */
export function stringContains(str, needle) {
  str = String(str);
  return str.indexOf(needle) !== -1;
}

/**
 * @param {string} str
 * @param {number} numCharactersToRemove
 *
 * @returns {string}
 */
export function removeCharactersFromEndOfString(str, numCharactersToRemove) {
  str = String(str);
  return str.substr(0, str.length - numCharactersToRemove);
}

/**
 * We do not check whether URL contains already url parameter, please use removeUrlParameter() if needed
 * before calling this method.
 * This method makes sure to append URL parameters before a possible hash. Will escape (encode URI component)
 * the set name and value
 *
 * @param {string} url
 * @param {string} name
 * @param {string} value
 *
 * @returns {string}
 */
export function addUrlParameter(url, name, value) {
  url = String(url);

  if (!value) {
    value = "";
  }

  let hashPos = url.indexOf("#");
  const urlLength = url.length;

  if (hashPos === -1) {
    hashPos = urlLength;
  }

  let baseUrl = url.substr(0, hashPos);
  const urlHash = url.substr(hashPos, urlLength - hashPos);

  if (baseUrl.indexOf("?") === -1) {
    baseUrl += "?";
  } else if (!stringEndsWith(baseUrl, "?")) {
    baseUrl += "&";
  }
  // nothing to if ends with ?

  return (
    baseUrl +
    encodeURIComponent(name) +
    "=" +
    encodeURIComponent(value) +
    urlHash
  );
}

/**
 * @param {string} url
 * @param {string} name
 *
 * @returns {string}
 */
export function removeUrlParameter(url, name) {
  url = String(url);

  if (
    url.indexOf("?" + name + "=") === -1 &&
    url.indexOf("&" + name + "=") === -1
  ) {
    // nothing to remove, url does not contain this parameter
    return url;
  }

  const searchPos = url.indexOf("?");
  if (searchPos === -1) {
    // nothing to remove, no query parameters
    return url;
  }

  let queryString = url.substr(searchPos + 1);
  let baseUrl = url.substr(0, searchPos);

  if (queryString) {
    let urlHash = "";
    const hashPos = queryString.indexOf("#");
    if (hashPos !== -1) {
      urlHash = queryString.substr(hashPos + 1);
      queryString = queryString.substr(0, hashPos);
    }

    let param;
    const paramsArr = queryString.split("&");
    let i = paramsArr.length - 1;

    for (i; i >= 0; i--) {
      param = paramsArr[i].split("=")[0];
      if (param === name) {
        paramsArr.splice(i, 1);
      }
    }

    const newQueryString = paramsArr.join("&");

    if (newQueryString) {
      baseUrl = baseUrl + "?" + newQueryString;
    }

    if (urlHash) {
      baseUrl += "#" + urlHash;
    }
  }

  return baseUrl;
}

/**
 * Extract parameter from URL
 *
 * @param {string} url
 * @param {string} name
 *
 * @returns {string}
 */
export function getUrlParameter(url, name) {
  const regexSearch = "[\\?&#]" + name + "=([^&#]*)";
  const regex = new RegExp(regexSearch);
  const results = regex.exec(url);
  return results ? safeDecodeWrapper(results[1]) : "";
}

/**
 * @param {string} text
 *
 * @returns {string}
 */
export function trim(text) {
  if (text && String(text) === text) {
    return text.replace(/^\s+|\s+$/g, "");
  }

  return text;
}

/**
 * UTF-8 encoding
 *
 * @param {string} argString
 *
 * @returns {string}
 */
export function utf8_encode(argString) {
  return unescape(encodeURIComponent(argString));
}

/************************************************************
 * sha1
 * - based on sha1 from http://phpjs.org/functions/sha1:512 (MIT / GPL v2)
 ************************************************************/

/**
 * @param {string} str
 *
 * @returns {string}
 */
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
    default:
      // Copy the 0 case
      i = 0x080000000;
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

/**
 * Fix-up URL when page rendered from search engine cache or translated page;
 * returning the actual page URL components, stripping any search engine junk
 * from the URL.
 *
 * @param {string} hostName
 * @param {string} href
 * @param {string} referrer
 *
 * @returns {string[]} "fixed" versions of the passed in parameters
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
    hostName.slice(0, 5) === "74.6." // Yahoo (via Inktomi 74.6.0.0/16)
  ) {
    href = document.links[0].href;
    hostName = getHostName(href);
  }

  return [hostName, href, referrer];
}

/**
 * Fix-up domain
 *
 * @param {string} domain
 *
 * @returns {string}
 */
export function domainFixup(domain) {
  let dl = domain.length;

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

/**
 * Title fixup
 *
 * @param {string | { text: string }} title
 *
 * @returns {string}
*/
export function titleFixup(title) {
  // @ts-ignore - title.text may not exist, depending on what was passed in.
  let _title = title?.text || title;

  if (!isString(title)) {
    const tmp = document.getElementsByTagName("title");

    if (tmp && isDefined(tmp[0])) {
      _title = tmp[0].text;
    }
  }

  return _title;
}

/**
 * @param {Node | ParentNode} node
 *
 * @returns {NodeListOf<ChildNode>}
 */
export function getChildrenFromNode(node) {
  if (!node) {
    new NodeList();
  }

  return node.childNodes;
}

/**
 * Checks if a node contains another node element within it.
 *
 * @param {Node} node - The node to check if it contains the other node.
 * @param {Node} containedNode - The node to check if it's contained within the first node.
 *
 * @returns {boolean} Returns true if the first node contains the other node, false otherwise.
 */
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

/**
 * Returns the first index at which a given element can be found in the array, or -1 if it is not present.
 *
 * @param {Array} theArray - The array to search in.
 * @param {any} searchElement - The element to search for within the array.
 *
 * @returns {number} Returns the index of the first occurrence of the specified element in the array, or -1 if not found.
 */
export function indexOfArray(theArray, searchElement) {
  if (!theArray) {
    return -1;
  }
  return theArray.indexOf(searchElement);
}

/**
 * Generates a UUID (Universally Unique Identifier) using the v4 variant.
 *
 * @returns {string} Returns a randomly generated UUID.
 */
export function uuidv4() {
  return crypto.randomUUID();
}

/**
 * Retrieves the current timestamp in seconds.
 *
 * @returns {number} Returns the current timestamp in seconds.
 */
export function getCurrentTimestampInSeconds() {
  return Math.floor(new Date().getTime() / 1000);
}

/**
 * Sorts the keys of an object alphabetically and returns a new object with the sorted keys.
 *
 * @param {Object} value - The object whose keys are to be sorted.
 *
 * @returns {Object|undefined} Returns a new object with sorted keys, or undefined if the input value is falsy or not an object.
 */
export function sortObjectsByKeys(value) {
  if (!value || !isObject(value)) {
    return;
  }

  const keys = Object.keys(value).sort();

  const normalized = {};

  for (const key of keys) {
    normalized[key] = value[key];
  }

  return normalized;
}

/**
 * Generates a unique identifier consisting of 6 random alphanumeric characters.
 *
 * @returns {string} Returns a unique identifier.
 */
export function generateUniqueId() {
  let id = "";
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const charLen = chars.length;

  for (let i = 0; i < 6; i++) {
    id += chars.charAt(Math.floor(Math.random() * charLen));
  }

  return id;
}

/**
 * Splits an array into chunks of a specified size.
 *
 * @param {Array} theArray - The array to be split into chunks.
 * @param {number} chunkSize - The size of each chunk.
 *
 * @returns {Array} Returns an array containing chunks of the original array.
 */
export function arrayChunk(theArray, chunkSize) {
  if (!chunkSize || chunkSize >= theArray.length) {
    return [theArray];
  }

  const chunks = [];

  for (let index = 0; index < theArray.length; index += chunkSize) {
    chunks.push(theArray.slice(index, index + chunkSize));
  }

  return chunks;
}

/**
 * Sets the expiration date and time for a global variable if it's not already set or if the new time is greater.
 *
 * @param {number} delay - The delay in milliseconds from the current time.
 */
export function setExpireDateTime(delay) {
  const now = new Date();
  const time = now.getTime() + delay;

  if (
    !eaveWindow.eave.expireDateTime ||
    time > eaveWindow.eave.expireDateTime
  ) {
    eaveWindow.eave.expireDateTime = time;
  }
}

/**
 * Checks if two host names are the same, considering aliases and wildcard subdomains.
 *
 * @param {string} hostName - The host name to compare.
 * @param {string} alias - The alias or domain to compare against.
 *
 * @returns {boolean} Returns true if the host names are the same, false otherwise.
 */
export function isSameHost(hostName, alias) {
  let offset;

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

/**
 * Checks if a path matches a path alias, supporting wildcards and case insensitivity.
 *
 * @param {string} path - The path to check.
 * @param {string} pathAlias - The path alias to match against.
 *
 * @returns {boolean} Returns true if the path matches the path alias, false otherwise.
 */
export function isSitePath(path, pathAlias) {
  if (!stringStartsWith(pathAlias, "/")) {
    pathAlias = "/" + pathAlias;
  }

  if (!stringStartsWith(path, "/")) {
    path = "/" + path;
  }

  let matchesAnyPath = pathAlias === "/" || pathAlias === "/*";

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
 *
 * @returns {string} query params to attach to a request URL
 */
export function argsToQueryParameters(args) {
  let qp = "";
  for (const key of Object.keys(args)) {
    qp += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(String(args[key]));
  }
  return qp;
}
