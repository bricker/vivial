function startCollecting({ clientId }: { clientId: string }) {
  // TODO: save client stuff and add a bunch of event listeners
  // TODO: add browser ext eslint plugins for vscode
  console.debug("eave extension collector started");
  // chrome.storage.local;
}

async function sendAtom() {
  try {
    const response = await fetch(`${eave_ingest_base_url}/public/ingest/extension?clientId=${clientId}`, {
      method: "POST",
      body: JSON.stringify(atoms),
    });

    if (!response.ok) {
      throw new Error(`Error! status: ${response.status}`);
    }
  } catch {
    // TODO: requeue to try batch again later?
  }
}
