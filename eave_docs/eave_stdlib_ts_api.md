## List Management API

### Get All Lists

```
GET /v1/lists
```

Returns all lists.

### Example Request

```javascript
fetch('/v1/lists', {
  method: 'GET',
})
```

### Example Response

```json
["TODO", "Personal", "Work", "Shopping"]
```

### Response Codes

**200**: The request was successful and the response body contains an array of lists.

---

### Get Specific List

```
GET /v1/lists/:list_id
```

Returns a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'GET',
})
```

### Example Response

```json
"Personal"
```

### Response Codes

**200**: The request was successful and the response body contains the requested list.

**404**: The requested list could not be found.

---

### Create List

```
POST /v1/lists
```

Creates a new list.

### Example Request

```javascript
fetch('/v1/lists', {
  method: 'POST',
  body: JSON.stringify({
    list: 'New List'
  })
})
```

### Response Codes

**201**: The list was successfully created.

---

### Update List

```
PATCH /v1/lists/:list_id
```

Updates a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'PATCH',
  body: JSON.stringify({
    list: 'Updated List'
  })
})
```

### Response Codes

**200**: The list was successfully updated.

**404**: The list to update could not be found.

---

### Delete List

```
DELETE /v1/lists/:list_id
```

Deletes a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'DELETE',
})
```

### Response Codes

**200**: The list was successfully deleted.

**404**: The list to delete could not be found.

---

## User Management API

### Get All Users

```
GET /v1/users
```

Returns all users.

### Example Request

```javascript
fetch('/v1/users', {
  method: 'GET',
})
```

### Example Response

```json
["Liam", "Lana", "Leilenah", "Bryan"]
```

### Response Codes

**200**: The request was successful and the response body contains an array of users.

---

### Get Specific User

```
GET /v1/users/:user_id
```

Returns a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'GET',
})
```

### Example Response

```json
"Lana"
```

### Response Codes

**200**: The request was successful and the response body contains the requested user.

**404**: The requested user could not be found.

---

### Create User

```
POST /v1/users
```

Creates a new user.

### Example Request

```javascript
fetch('/v1/users', {
  method: 'POST',
  body: JSON.stringify({
    user: 'New User'
  })
})
```

### Response Codes

**201**: The user was successfully created.

---

### Update User

```
PATCH /v1/users/:user_id
```

Updates a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'PATCH',
  body: JSON.stringify({
    user: 'Updated User'
  })
})
```

### Response Codes

**200**: The user was successfully updated.

**404**: The user to update could not be found.

---

### Delete User

```
DELETE /v1/users/:user_id
```

Deletes a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'DELETE',
})
```

### Response Codes

**200**: The user was successfully deleted.

**404**: The user to delete could not be found.

<br />

