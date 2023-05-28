import qs from 'querystring';
import api, { route } from '@forge/api';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import { JsonObject, WebTriggerRequestPayload, WebTriggerResponsePayload } from '../types';
import { makeResponse } from '../response';

export default async function createDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  eaveLogger.info('createDocument', request);

  if (request.headers === undefined || request.body === undefined) {
    return makeResponse({ statusCode: 400 });
  }

  const requestData = JSON.parse(request.body);
  const {
    title: documentTitle,
    body: documentBody,
  } = requestData;

  const spaceKey = 'EAVE';
  const query = qs.stringify({
    keys: [spaceKey],
    type: 'global',
    status: 'current',
  });

  // https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
  const spacesResponse = await api
    .asApp()
    .requestConfluence(route`/wiki/api/v2/spaces?${query}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });
  console.log('spacesResponse', spacesResponse.status, spacesResponse.statusText);

  // TODO: Surely there's a cleaner way to do this...
  const spacesResults = <JsonObject> await spacesResponse.json();
  eaveLogger.debug('spacesResults', spacesResults);
  const spaces = <JsonObject[]>spacesResults['results'];
  const space = spaces?.find((s) => s['key'] === spaceKey);

  if (!space) {
    return makeResponse({ statusCode: 400, statusText: `Space not found: ${spaceKey}` });
  }

  const bodyData = {
    spaceId: space['id'],
    status: 'current',
    title: documentTitle,
    parentId: '',
    body: {
      representation: 'storage',
      value: documentBody,
    },
  };
  eaveLogger.debug('bodyData', bodyData);

  // https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post
  const response = await api
    .asApp()
    .requestConfluence(route`/wiki/api/v2/pages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(bodyData),
    });
  console.log('response', response.status, response.statusText);

  const pageResult = <JsonObject> await response.json();
  eaveLogger.debug('pageResult', pageResult);

  return makeResponse({
    statusCode: 200,
    body: pageResult,
  });
}
