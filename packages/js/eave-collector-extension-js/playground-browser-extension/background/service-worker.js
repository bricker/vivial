import { startCollecting } from "@eave-fyi/eave-collector-extension";

console.log("[eave] service-worker.js loaded");

startCollecting({ clientId: "some_client_id" });

addEventListener("unhandledrejection", async (event) => {
  console.error(event);
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed");
});

// // Throw an exception after a timeout to trigger an exception analytics event
// setTimeout(throwAnException, 2000);

async function throwAnException() {
  throw new Error("👋 I'm an error");
}
