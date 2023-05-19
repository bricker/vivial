import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { signBase64, getKey } from '@eave-fyi/eave-stdlib-ts/src/signing.js';

async function run() {
  const data = JSON.stringify({
    "test": "data",
  });

  const key = getKey(EaveOrigin.eave_github_app);
  const sig = await signBase64(key, data);

  console.log(sig);
}

run();
