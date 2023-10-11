## Jira Webhook Event

```
POST /events
```

This API endpoint receives webhook events from Jira. It specifically handles the "comment_created" event. When a comment is created in Jira, this endpoint is triggered. It checks if the comment author is an app or a user. If it's a user, it checks if the user mentioned Eave in the comment. If Eave is mentioned, it logs the event, cleans the comment body, determines the intent of the comment, and performs a document search based on the intent. If the intent is to search, it responds with the search results.

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
      body: 'Eave, can you find the documentation for this feature?',
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

**200**: The request was successful. This response code will be returned after the event is processed.

**400**: Bad Request. This response code will be returned if the payload is missing the issue or if there is no teamId available.

<br />

