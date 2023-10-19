## GitHub Events Handler

```
POST /github/events
```

This API endpoint is used to handle incoming GitHub webhook events. It validates the headers of the incoming request, verifies the signature, and if valid, it creates a task for the event in the background. If the event is not supported, it logs a warning and sends a 200 OK response.

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

**200**: The request was successful, and the event is either handled or not supported.

**400**: The request was unsuccessful due to missing header data from GitHub or signature verification failure.

<br />

