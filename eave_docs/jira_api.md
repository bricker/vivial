## Webhook Event Handler

```
POST /events
```

This API endpoint receives webhook events, specifically from Jira. It handles the "comment_created" event by checking if the comment author is an app or a user. If the comment author is a user, it checks if the user mentioned Eave in the comment. If Eave is mentioned, it logs the event, cleans the comment body, determines the intent of the comment, and if the intent is to search, it performs a document search and posts a comment with the search results.

### Path Parameters

None

### Example Request

```javascript
fetch('http://localhost:3000/events', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    webhookEvent: 'comment_created',
    issue: { id: '123' },
    comment: {
      author: { accountType: 'user' },
      body: 'Eave, can you find documentation about jelly beans?',
    },
  }),
});
```

### Example Response

```javascript
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful. This response code will be returned after the event is processed, regardless of whether Eave was mentioned in the comment or not.

**400**: Bad Request. This response code will be returned if the payload is missing the issue or if there is no teamId available.

<br />

