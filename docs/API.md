# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "requires_2fa": false
}
```

#### POST /auth/verify-2fa
Verify 2FA code.

**Request:**
```json
{
  "temp_token": "eyJ0eXAi...",
  "code": "123456"
}
```

#### GET /auth/me
Get current user information. **[Protected]**

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "is_active": true,
  "is_superuser": false
}
```

### Projects

#### GET /projects/
Get all projects with pagination.

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 10, max: 100)
- `featured` (optional): true/false

**Response:**
```json
[
  {
    "id": 1,
    "title": "Project Title",
    "description": "Description",
    "technologies": "Python, FastAPI",
    "featured": true,
    "images": [],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /projects/{project_id}
Get single project with details.

**Response:**
```json
{
  "id": 1,
  "title": "Project Title",
  "description": "Description",
  "content": "Full content",
  "technologies": "Python, FastAPI",
  "github_url": "https://github.com/user/repo",
  "demo_url": "https://demo.example.com",
  "featured": true,
  "images": [],
  "videos": [],
  "comments": [],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /projects/
Create new project. **[Admin Only]**

#### PUT /projects/{project_id}
Update project. **[Admin Only]**

#### DELETE /projects/{project_id}
Delete project. **[Admin Only]**

### Blog

#### GET /blog/
Get all blog posts.

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 10)
- `published` (default: true)

#### GET /blog/{slug}
Get blog post by slug.

#### POST /blog/
Create blog post. **[Admin Only]**

#### PUT /blog/{post_id}
Update blog post. **[Admin Only]**

#### DELETE /blog/{post_id}
Delete blog post. **[Admin Only]**

### Reactions

#### POST /reactions/{entity_type}/{entity_id}
Add or update reaction.

**entity_type:** `project` or `blog_post`

**Request:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "reaction_type": "like"
}
```

**Reaction Types:**
- `like`
- `love`
- `congratulations`

#### GET /reactions/{entity_type}/{entity_id}/summary
Get reaction summary for entity.

**Response:**
```json
{
  "total_reactions": 10,
  "like_count": 5,
  "love_count": 3,
  "congratulations_count": 2,
  "user_reaction": "like"
}
```

### Contact

#### POST /contact/
Send contact message.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Message content"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

## Rate Limiting

Public endpoints are rate limited to prevent abuse:
- Contact form: 5 requests per minute
- Authentication: 10 requests per minute

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /api/v1/projects/?page=1&page_size=10
```

**Response includes:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10,
  "has_next": true,
  "has_prev": false
}
```