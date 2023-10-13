## GitHub Events Endpoint

```
POST /github/events
```

This API endpoint is used to receive and process GitHub webhook events. It validates the headers of the incoming request, verifies the signature, and if valid, it creates a task to handle the event.

### Path Parameters

None

### Headers

**x-github-delivery** (string) *required* - The unique ID of the delivery.

**x-github-event** (string) *required* - The name of the event that triggered the delivery.

**x-hub-signature-256** (string) *required* - The HMAC hex digest of the response body. This header will be sent if the webhook is configured with a secret.

**x-github-hook-installation-target-id** (string) *required* - The ID of the app that received the event.

### Example Request

```javascript
fetch('http://localhost:3000/github/events', {
  method: 'POST',
  headers: {
    'x-github-delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
    'x-github-event': 'push',
    'x-hub-signature-256': 'sha1=7d38cdd689735b008b3c702edd92eea23791c5f6',
    'x-github-hook-installation-target-id': '123456'
  },
  body: JSON.stringify({payload})
})
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful and the event is being processed.

**400**: The request was unsuccessful due to missing or invalid headers.

<br />

