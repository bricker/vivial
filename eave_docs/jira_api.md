## Webhook Event Handler

```
POST /
```

This API endpoint is used to handle webhook events. It authenticates the request, logs the received event, and then processes the event based on its type. Currently, it only handles "comment_created" events. For these events, it invokes the `commentCreatedEventHandler` function. If the event type is not recognized, it logs a warning and sends a 200 status response.

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
    // ...other properties of the webhook event...
  }),
});
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful. This code is returned after the event has been processed, or if the event type is not recognized.

**400**: The request was malformed. This code is returned if the payload of a "comment_created" event does not contain an issue, or if no teamId is available.

<br />

