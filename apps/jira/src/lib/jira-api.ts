import api, { route } from '@forge/api';
import { Issue, Content, ContentType } from '../types.js';

export async function addComment(issue: Issue, content: Content[]) {
  const requestUrl = route`/rest/api/3/issue/${issue.id}/comment`;

  const response = await api
    .asApp()
    .requestJira(requestUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        body: {
          type: ContentType.doc,
          version: 1,
          content,
        },
      }),
    });

  // Error checking: the Jira issue comment Rest API returns a 201 if the request is successful
  if (response.status !== 201) {
    console.log(response.status);
    throw new Error(`Unable to add comment to issueKey ${issue.key} Status: ${response.status}.`);
  }

  return response.json();
}

// const fetchCommentsForIssue = async (issueIdOrKey) => {
//   const res = await api
//     .asUser()
//     .requestJira(route`/rest/api/3/issue/${issueIdOrKey}/comment`);

//   const data = await res.json();
//   return data.comments;
// };
