## Webhook Event Receiver

```
POST /events
```

This API endpoint receives webhook events and logs them.

### Path Parameters

None

### Example Request

```javascript
fetch('/events', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ event: 'exampleEvent' })
});
```

### Example Response

No response body is returned for this endpoint.

### Response Codes

**200**: The webhook event was received and logged successfully.

**401**: Unauthorized. The request was not authenticated.

<br />

