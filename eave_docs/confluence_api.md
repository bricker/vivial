## Webhook Event Receiver

```
POST /events
```

This API endpoint is used to receive webhook events. It authenticates the request, logs the event, and does not return a response.

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

No response is returned from this endpoint.

### Response Codes

**200**: This response code will be returned if the webhook event is received successfully.

<br />

## Query Spaces

```
POST /api/spaces/query
```

This endpoint is used to query available spaces in Confluence.

### Path Parameters

None

### Example Request

```javascript
fetch('/api/spaces/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### Example Response

```json
{
  "confluence_spaces": [
    {
      "id": "1",
      "key": "TST",
      "name": "Test Space",
      "description": "This is a test space"
    },
    {
      "id": "2",
      "key": "PRD",
      "name": "Production Space",
      "description": "This is a production space"
    }
  ]
}
```

### Response Codes

**200**: The request was successful and the available spaces are returned in the response.

---

## Search Content

```
POST /api/content/search
```

This endpoint is used to search for content in Confluence.

### Path Parameters

None

### Example Request

```javascript
fetch('/api/content/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    search_params: {
      space_key: 'TST',
      text: 'Test'
    }
  })
})
```

### Example Response

```json
{
  "results": [
    {
      "id": "1",
      "title": "Test Document",
      "space": {
        "key": "TST"
      },
      "body": {
        "storage": {
          "value": "<p>This is a test document</p>"
        }
      }
    }
  ]
}
```

### Response Codes

**200**: The request was successful and the search results are returned in the response.

---

## Create Content

```
POST /api/content/create
```

This endpoint is used to create new content in Confluence.

### Path Parameters

None

### Example Request

```javascript
fetch('/api/content/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    document: {
      title: 'New Document',
      content: '<p>This is a new document</p>'
    },
    confluence_destination: {
      space_key: 'TST'
    }
  })
})
```

### Example Response

```json
{
  "content": {
    "id": "1",
    "title": "New Document",
    "space": {
      "key": "TST"
    },
    "body": {
      "storage": {
        "value": "<p>This is a new document</p>"
      }
    }
  }
}
```

### Response Codes

**200**: The request was successful and the newly created content is returned in the response.

---

## Update Content

```
POST /api/content/update
```

This endpoint is used to update existing content in Confluence.

### Path Parameters

None

### Example Request

```javascript
fetch('/api/content/update', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: {
      id: '1',
      body: '<p>This is an updated document</p>'
    }
  })
})
```

### Example Response

```json
{
  "content": {
    "id": "1",
    "title": "New Document",
    "space": {
      "key": "TST"
    },
    "body": {
      "storage": {
        "value": "<p>This is an updated document</p>"
      }
    }
  }
}
```

### Response Codes

**200**: The request was successful and the updated content is returned in the response.

---

## Delete Content

```
POST /api/content/delete
```

This endpoint is used to delete existing content in Confluence.

### Path Parameters

None

### Example Request

```javascript
fetch('/api/content/delete', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: {
      content_id: '1'
    }
  })
})
```

### Example Response

```json
{}
```

### Response Codes

**200**: The request was successful and the content was deleted.

<br />

