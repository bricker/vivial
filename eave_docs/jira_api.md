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

**200**: The request was successful. This response code will be returned even if the webhook event is not handled.

**400**: The request was unsuccessful due to missing or incorrect data in the payload.

<br />

