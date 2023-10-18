## Webhook Event Handler

```
POST /events
```

This API endpoint is used to handle webhook events. It receives a webhook event, logs the event, and then processes it based on the type of the event. If the event is a "comment_created" event, it triggers the `commentCreatedEventHandler` function. If the event type is not handled, it logs a warning and sends a 200 status response.

### Path Parameters

None

### Example Request

```javascript
fetch('http://localhost:3000/events', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    webhookEvent: 'comment_created',
    // other event data...
  })
});
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The webhook event was received and processed successfully.

**400**: The webhook event was not processed successfully due to missing or incorrect data in the payload.

<br />

