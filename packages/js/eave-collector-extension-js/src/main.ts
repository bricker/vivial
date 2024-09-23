function startCollecting() {
  // TODO: save client stuff and add a bunch of event listeners
  // TODO: add browser ext eslint plugins for vscode
  chrome.storage.local
}

async function sendAtom() {
  try {
    const response = await fetch(`${eave_ingest_base_url}/public/ingest/extension`, {
      method: "POST",
      body: JSON.stringify(),
      headers: {
        "eave-client-id": client_id,
        "eave-client-secret": client_secret,
      },
    });

    if (!response.ok) {
      throw new Error(`Error! status: ${response.status}`);
    }
  } catch {
    // TODO: requeue to try batch again later?
  }
}
