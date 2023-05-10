import qs from 'querystring';
import api, { route } from '@forge/api';
import { JsonObject, WebTriggerRequestPayload, WebTriggerResponsePayload } from './types.js';

// FIXME:
const SPACEKEY = 'ED';

// https://developer.atlassian.com/platform/forge/events-reference/web-trigger/
export async function createDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  console.log('request', request);

  if (request.headers === undefined || request.body === undefined) {
    return _makeResponse({ statusCode: 400 });
  }

  const givenSecret = request.headers['eave-secret']?.[0];
  const actualSecret = process.env['EAVE_FORGE_SHARED_SECRET'];
  if (!givenSecret || !actualSecret || givenSecret !== actualSecret) {
    return _makeResponse({ statusCode: 400 });
  }

  const requestData = JSON.parse(request.body);
  const { title: documentTitle, body: documentBody } = requestData;

  const query = qs.stringify({
    keys: [SPACEKEY],
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
  const spacesResults = <JsonObject>await spacesResponse.json();
  console.log('spacesResults', spacesResults);
  const spaces = <JsonObject[]>spacesResults['results'];
  const space = spaces?.find((s) => s['key'] === SPACEKEY);

  if (!space) {
    return _makeResponse({ statusCode: 400, statusText: `Space not found: ${SPACEKEY}` });
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
  console.log('bodyData', bodyData);

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

    const pageResult = <JsonObject>await response.json();
    console.log('pageResult', pageResult);

  return _makeResponse({
    statusCode: 200,
    body: pageResult,
  });

  // const requestData = <WebTriggerRequest>JSON.parse(request);
  // if (requestData.body === undefined) {
  //   console.warn('requestData.body is missing; abort.');
  //   return;
  // }

  // const requestBody = JSON.parse(requestData.body);

  // const documentTitle = requestBody.title;
  // const documentBody = requestBody.body;

  // const requestUrl = route`/wiki/api/v2/pages`;

  // const bodyData = {
  //   spaceId: 'ED',
  //   status: 'current',
  //   title: documentTitle,
  //   parentId: '',
  //   body: {
  //     representation: 'storage',
  //     value: documentBody,
  //   },
  // };

  // const response = await api
  //   .asApp()
  //   .requestConfluence(requestUrl, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       Accept: 'application/json',
  //     },
  //     body: JSON.stringify(bodyData),
  //   });

  // console.log(response);
  // // // Error checking: the Jira issue comment Rest API returns a 201 if the request is successful
  // // if (response.status !== 201) {
  // //   throw new Error(`Unable to add comment to issueKey ${issue.key} Status: ${response.status}.`);
  // // }

  // return response.json();
}

export async function updateDocument(): Promise<void> {
}

export async function archiveDocument(): Promise<void> {
}

// export async function (issue: Issue, content: Content[]) {
//   const requestUrl = route`/rest/api/3/issue/${issue.id}/comment`;

//   const response = await api
//     .asApp()
//     .requestConfluence(requestUrl, {
//       method: 'POSTS',
//       headers: {
//         'Content-Type': 'application/json',
//         Accept: 'application/json',
//       },
//       body: JSON.stringify({
//         body: {
//           type: ContentType.doc,
//           version: 1,
//           content,
//         },
//       }),

//     });

//   // Error checking: the Jira issue comment Rest API returns a 201 if the request is successful
//   if (response.status !== 201) {
//     console.log(response.status);
//     throw new Error(`Unable to add comment to issueKey ${issue.key} Status: ${response.status}.`);
//   }

//   return response.json();
// }

// const fetchCommentsForIssue = async (issueIdOrKey) => {
//   const res = await api
//     .asUser()
//     .requestJira(route`/rest/api/3/issue/${issueIdOrKey}/comment`);

//   const data = await res.json();
//   return data.comments;
// };

function _makeResponse(
  { statusCode = 200, statusText, body = {} }:
  { statusCode?: number, statusText?: string, body?: {[key: string]: any} }): WebTriggerResponsePayload {

  return {
    body: JSON.stringify(body),
    headers: {
      'Content-Type': ['application/json'],
    },
    statusCode,
    statusText: statusText || `${statusCode}`,
  };
}