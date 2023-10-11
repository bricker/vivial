## Github Events Endpoint

```
POST /github/events
```

This API endpoint is used to receive and process Github webhook events. It validates the Github webhook headers, verifies the signature, and if valid, creates a task from the request to handle the event.

### Path Parameters

None

### Headers

**x-github-delivery** (string) *required* - The unique ID of the delivery.

**x-github-event** (string) *required* - The name of the event that triggered the webhook.

**x-hub-signature-256** (string) *required* - The signature of the webhook payload, used to verify the request.

**x-github-hook-installation-target-id** (string) *required* - The ID of the Github App installation that the event is associated with.

### Example Request

```javascript
fetch('http://localhost:3000/github/events', {
  method: 'POST',
  headers: {
    'x-github-delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
    'x-github-event': 'push',
    'x-hub-signature-256': 'sha256=4864d2759938a15468b5df9e3f605dbedfe11c678733299d7f8a3c2f877b621c',
    'x-github-hook-installation-target-id': '123456'
  },
  body: JSON.stringify({/* event payload */})
})
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful and the event is being processed.

**400**: The request was unsuccessful due to missing or invalid header data, or the signature verification failed.

<br />

