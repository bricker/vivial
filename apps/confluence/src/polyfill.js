/* eslint-disable no-global-assign */
// The Forge app runs in a Node-ish environment, but with limitations.
// See here for more info:  https://developer.atlassian.com/platform/forge/runtime-reference/

import fetch from 'node-fetch';

if (global.fetch === undefined) {
  global.fetch = fetch;
}

if (global.importScripts === undefined) {
  global.importScripts = () => {
    console.warn('  ');
  };
}

if (process.argv === undefined) {
  process.argv = [];
}

if (global.setTimeout === undefined) {
  global.setTimeout = () => {
    console.warn('setTimeout called, but is unsupported in the current environment');
  };
}

if (global.setImmediate === undefined) {
  global.setImmediate = () => {
    console.warn('setImmediate called, but is unsupported in the current environment');
  };
}

if (global.setInterval === undefined) {
  global.setInterval = () => {
    console.warn('setInterval called, but is unsupported in the current environment');
  };
}
