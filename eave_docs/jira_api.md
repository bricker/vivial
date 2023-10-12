## Webhook Event Handler

```
POST /
```

This API endpoint is used to handle webhook events. It authenticates the request, logs the event, and then processes the event based on its type. Currently, it only handles "comment_created" events. For these events, it checks if the comment author is an app, if Eave is mentioned in the comment, and if the intent of the comment is to search for documentation. If all these conditions are met, it searches for relevant documents and posts a comment with the search results.

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
      body: 'Can you find documentation about jelly beans? [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]'
    }
  })
});
```

### Example Response

```javascript
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful. This code is returned after the event is processed, even if the event type is not handled or if the conditions for processing the "comment_created" event are not met.

**400**: The request was not successful. This code is returned if the "comment_created" event does not include an issue in the payload, if there is no teamId available, or if the comment author is an app.

<br />

