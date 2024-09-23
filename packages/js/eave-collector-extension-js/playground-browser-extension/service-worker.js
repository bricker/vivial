// import Analytics from './scripts/google-analytics.js';

import eave from '@eave-fyi/extension-collector';

eave.startCollecting({ clientId: "xyz" })

console.log("[eave] service-worker.js loaded")

addEventListener('unhandledrejection', async (event) => {
  console.error(event);
  // Analytics.fireErrorEvent(event.reason);
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed");
  // Analytics.fireEvent('install');
});

// // Throw an exception after a timeout to trigger an exception analytics event
// setTimeout(throwAnException, 2000);

async function throwAnException() {
  throw new Error("👋 I'm an error");
}
