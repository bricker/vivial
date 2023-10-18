## GitHub Events Handler

```
POST /github/events
```

This API endpoint is used to handle GitHub events. It validates the GitHub webhook headers, verifies the signature, and if valid, it creates a task from the request and sends it to a queue for processing.

### Path Parameters

None

### Headers

**x-github-delivery** (string) *required* - The unique ID of the delivery.

**x-github-event** (string) *required* - The name of the event that triggered the webhook.

**x-hub-signature-256** (string) *required* - The signature for the webhook payload, used to verify the sender.

**x-github-hook-installation-target-id** (string) *required* - The ID of the GitHub App installation that the event is related to.

### Example Request

```javascript
fetch('http://localhost:3000/github/events', {
  method: 'POST',
  headers: {
    'x-github-delivery': '72d3162e-cc78-11e3-81ab-4c9367dc0958',
    'x-github-event': 'push',
    'x-hub-signature-256': 'sha256=4864d2759938a15468b5df9e3f6052e4b175e5f206e55fcef3c1af731aea85f1',
    'x-github-hook-installation-target-id': '123456'
  },
  body: JSON.stringify({/*...payload...*/})
})
```

### Example Response

```
HTTP/1.1 200 OK
```

### Response Codes

**200**: The request was successful and the event is supported.

**400**: The request was unsuccessful due to missing header data from GitHub or signature verification failure.

<br />

