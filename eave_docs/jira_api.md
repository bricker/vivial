## Webhook Event Handler

```
POST /
```

This API endpoint is used to handle webhook events. It authenticates the request, logs the event, and then processes the event based on its type. Currently, it only handles "comment_created" events. For these events, it checks if the comment author is an app, if Eave is mentioned in the comment, and if the comment's intent is to search. If all these conditions are met, it performs a document search and posts a comment with the search results.

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

```json
{
  "status": 200
}
```

### Response Codes

**200**: The request was successful. This code is returned after the event is processed, regardless of whether Eave was mentioned in the comment or if the comment's intent was to search.

**400**: The request was unsuccessful. This code is returned if the payload is missing the issue or if there is no teamId available.

<br />

