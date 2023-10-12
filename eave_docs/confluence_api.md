## Webhook Event Receiver

```
POST /events
```

This API endpoint is used to receive webhook events. It authenticates the request using the addon middleware, logs the event, and does not return a response.

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

This endpoint does not return a response.

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

**200**: The request was successful and the available spaces are returned.

**500**: An error occurred while processing the request.

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
      "title": "Test Page",
      "space": {
        "key": "TST"
      },
      "body": {
        "storage": {
          "value": "<p>This is a test page</p>"
        }
      }
    }
  ]
}
```

### Response Codes

**200**: The request was successful and the search results are returned.

**500**: An error occurred while processing the request.

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
      title: 'New Page',
      content: '<p>This is a new page</p>'
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
    "id": "2",
    "title": "New Page",
    "space": {
      "key": "TST"
    },
    "body": {
      "storage": {
        "value": "<p>This is a new page</p>"
      }
    }
  }
}
```

### Response Codes

**200**: The request was successful and the new content is returned.

**400**: The specified space does not exist or does not have a homepage.

**500**: An error occurred while processing the request.

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
      id: '2',
      body: '<p>This is an updated page</p>'
    }
  })
})
```

### Example Response

```json
{
  "content": {
    "id": "2",
    "title": "New Page",
    "space": {
      "key": "TST"
    },
    "body": {
      "storage": {
        "value": "<p>This is an updated page</p>"
      }
    }
  }
}
```

### Response Codes

**200**: The request was successful and the updated content is returned.

**500**: The specified content does not exist or an error occurred while processing the request.

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
      content_id: '2'
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

**500**: An error occurred while processing the request.

<br />

