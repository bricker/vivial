## Webhook Event Handler

```
POST /
```

This API endpoint is used to handle webhook events. It authenticates the request, logs the received webhook event, and then processes the event based on its type. Currently, it only handles the "comment_created" event. If the event is not handled, it logs a warning and sends a 200 status response.

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
    // other necessary data
  }),
});
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: This response code will be returned if the webhook event is successfully received and processed, or if the event type is not handled.

**400**: This response code will be returned if there is an error in the payload of the "comment_created" event.

<br />

