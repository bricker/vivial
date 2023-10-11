## Webhook Event Handler

```
POST /
```

This API endpoint is used to handle webhook events. It authenticates the request, logs the event, and then processes the event based on its type. Currently, it only handles "comment_created" events. For these events, it checks if the comment author is an app, if Eave is mentioned in the comment, and if the intent of the comment is to search for something. If all these conditions are met, it performs a document search and posts a comment with the search results.

### Path Parameters

None

### Example Request

```javascript
fetch('http://localhost:3000/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    webhookEvent: 'comment_created',
    issue: { id: '123' },
    comment: {
      author: { accountType: 'user' },
      body: 'Eave, can you find the documentation for this feature?',
    },
  }),
});
```

### Example Response

```javascript
{
  "status": 200
}
```

### Response Codes

**200**: The request was successful. This code is returned after the event is processed, regardless of whether Eave was mentioned in the comment or not.

**400**: The request was malformed. This code is returned if the payload does not contain an issue or if there is no teamId available.

<br />

