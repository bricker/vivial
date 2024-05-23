// @ts-check

import * as Types from "./types.mjs"; // eslint-disable-line no-unused-vars


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
 * Get page referrer
 *
 * @returns {string}
 */
export function getReferrer() {
  return window.top?.document.referrer || window.parent.document.referrer || document.referrer;
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
 * Helper for typechecking
 *
 * @param {Node} node
 *
 * @returns {Element | null}
 */
export function castNodeToElement(node) {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {Element} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {Node} node
 *
 * @returns {HTMLElement | null}
 */
export function castNodeToHtmlElement(node) {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {HTMLElement} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {EventTarget | null} target
 *
 * @returns {HTMLElement | null}
 */
export function castEventTargetToHtmlElement(target) {
  if (!target) {
    return null;
  }

  // We're given an EventTarget, which is an interface implemented by many things, commonly Window or Node.
  // If this function is being called, then the caller should be pretty sure that the event target is an HTMLElement.
  // @ts-ignore
  const /** @type {Node} */ node = (target);

  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {HTMLElement} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {PerformanceEntry} entry
 *
 * @returns {PerformanceNavigationTiming | null}
 */
export function castPerformanceEntryToNavigationTiming(entry) {
  if (entry.entryType === "navigation") {
    const timing = /** @type {PerformanceNavigationTiming} */ (entry);
    return timing;
  } else {
    return null;
  }
}

/**
 * @param {Element} element
 *
 * @returns {{[key:string]: string}}
 */
export function getElementAttributes(element) {
  const /** @type {{[key:string]:string}} */ attrs = {};

  for (const attr of element.attributes) {
    attrs[attr.name] = attr.value;
  }

  return attrs;
}