import { webTrigger } from '@forge/api';
import { InstalledAppEventPayload, UpgradedAppEventPayload } from './types.js';

// These MUST exactly match the webtrigger keys in manifest.yml
const WEBTRIGGER_KEYS = [
  'webtrigger-createDocument',
  'webtrigger-updateDocument',
  'webtrigger-archiveDocument',
]

async function installedAppEventHandler(request: InstalledAppEventPayload) {
  for await (const key of WEBTRIGGER_KEYS) {
    const response = await webTrigger.getUrl(key);


  }
}

async function upgradedAppEventHandler() {

}