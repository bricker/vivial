import fetch from 'node-fetch';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins';
import { signBase64, getKey } from '@eave-fyi/eave-stdlib-ts/src/signing';
import { buildMessageToSign } from '@eave-fyi/eave-stdlib-ts/src/lib/requests';

async function run() {
  const data = JSON.stringify({
    test: 'data',
  });

  const rid = 'any';
  const msg = buildMessageToSign(
    'POST',
    'http://apps.eave.run:8080/github/api/content',
    rid,
    'eave_slack_app',
    data,
  );

  console.log(msg); /* eslint-ignore */

  const key = getKey(EaveOrigin.eave_slack_app);
  const sig = await signBase64(key, msg);

  console.log(sig); /* eslint-ignore */

  const r = await fetch('http://apps.eave.run:8080/github/api/content', {
    method: 'POST',
    headers: {
      'eave-origin': 'eave_slack_app',
      'eave-signature': sig,
      'content-type': 'application/json',
      'eave-request-id': rid,
    },
    body: data,
  });

  console.log(r); /* eslint-ignore */
}

run();
