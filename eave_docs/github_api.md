## GitHub Events Endpoint

```
POST /github/events
```

This API endpoint is used to receive and process GitHub webhook events. It validates the headers of the incoming request, verifies the signature, and if valid, it creates a task for the event handler to process the event.

### Path Parameters

None

### Example Request

```javascript
fetch('http://localhost:3000/github/events', {
  method: 'POST',
  headers: {
    'x-github-delivery': 'delivery_id',
    'x-github-event': 'event_name',
    'x-hub-signature-256': 'signature',
    'x-github-hook-installation-target-id': 'app_id'
  },
  body: JSON.stringify({ action: 'created' })
})
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful and the event is supported and will be processed.

**400**: The request was unsuccessful due to missing header data from GitHub or signature verification failure.

<br />

