import * as config from "./compile-config";

export function startCollecting({ clientId }: { clientId: string }) {
  // TODO: save client stuff and add a bunch of event listeners
  // TODO: add browser ext eslint plugins for vscode
  console.debug("eave extension collector started", clientId, config);
  // chrome.storage.local;
}

