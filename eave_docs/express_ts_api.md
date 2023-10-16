## List Management API

### Get All Lists

```
GET /v1/lists
```

This endpoint retrieves all lists.

### Example Request

```javascript
fetch('/v1/lists', {
  method: 'GET',
});
```

### Example Response

```json
["TODO", "Personal", "Work", "Shopping"]
```

### Response Codes

**200**: The request was successful and the list of all lists is returned.

---

### Get Specific List

```
GET /v1/lists/:list_id
```

This endpoint retrieves a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'GET',
});
```

### Example Response

```json
"Personal"
```

### Response Codes

**200**: The request was successful and the list is returned.

**404**: The list with the provided ID does not exist.

---

### Create List

```
POST /v1/lists
```

This endpoint creates a new list.

### Example Request

```javascript
fetch('/v1/lists', {
  method: 'POST',
  body: JSON.stringify({
    list: 'New List'
  })
});
```

### Response Codes

**201**: The list was successfully created.

---

### Update List

```
PATCH /v1/lists/:list_id
```

This endpoint updates a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'PATCH',
  body: JSON.stringify({
    list: 'Updated List'
  })
});
```

### Response Codes

**200**: The list was successfully updated.

**404**: The list with the provided ID does not exist.

---

### Delete List

```
DELETE /v1/lists/:list_id
```

This endpoint deletes a specific list by its ID.

### Path Parameters

**list_id** (integer) *required* - The ID of the list.

### Example Request

```javascript
fetch('/v1/lists/1', {
  method: 'DELETE',
});
```

### Response Codes

**200**: The list was successfully deleted.

**404**: The list with the provided ID does not exist.

---

## User Management API

### Get All Users

```
GET /v1/users
```

This endpoint retrieves all users.

### Example Request

```javascript
fetch('/v1/users', {
  method: 'GET',
});
```

### Example Response

```json
["Liam", "Lana", "Leilenah", "Bryan"]
```

### Response Codes

**200**: The request was successful and the list of all users is returned.

---

### Get Specific User

```
GET /v1/users/:user_id
```

This endpoint retrieves a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'GET',
});
```

### Example Response

```json
"Lana"
```

### Response Codes

**200**: The request was successful and the user is returned.

**404**: The user with the provided ID does not exist.

---

### Create User

```
POST /v1/users
```

This endpoint creates a new user.

### Example Request

```javascript
fetch('/v1/users', {
  method: 'POST',
  body: JSON.stringify({
    user: 'New User'
  })
});
```

### Response Codes

**201**: The user was successfully created.

---

### Update User

```
PATCH /v1/users/:user_id
```

This endpoint updates a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'PATCH',
  body: JSON.stringify({
    user: 'Updated User'
  })
});
```

### Response Codes

**200**: The user was successfully updated.

**404**: The user with the provided ID does not exist.

---

### Delete User

```
DELETE /v1/users/:user_id
```

This endpoint deletes a specific user by their ID.

### Path Parameters

**user_id** (integer) *required* - The ID of the user.

### Example Request

```javascript
fetch('/v1/users/1', {
  method: 'DELETE',
});
```

### Response Codes

**200**: The user was successfully deleted.

**404**: The user with the provided ID does not exist.

<br />

