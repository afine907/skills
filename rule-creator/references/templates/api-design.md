---
paths: ["src/routes/**/*", "src/api/**/*", "pages/api/**/*", "app/api/**/*"]
---

# API Design Conventions

## RESTful Principles

### URL Structure
- Use nouns, not verbs: `/users` not `/getUsers`
- Use plural nouns: `/users` not `/user`
- Nest resources for relationships: `/users/:id/posts`

```typescript
// ✅ Good
GET    /api/users           // List users
POST   /api/users           // Create user
GET    /api/users/:id       // Get user
PUT    /api/users/:id       // Update user
DELETE /api/users/:id       // Delete user
GET    /api/users/:id/posts // Get user's posts

// ❌ Avoid
GET    /api/getUsers
POST   /api/createUser
GET    /api/user/:id
```

### HTTP Methods
- `GET` — Read (no side effects)
- `POST` — Create
- `PUT` — Full update
- `PATCH` — Partial update
- `DELETE` — Remove

### Status Codes
- `200` — Success
- `201` — Created
- `204` — No Content (successful delete)
- `400` — Bad Request (validation error)
- `401` — Unauthorized
- `403` — Forbidden
- `404` — Not Found
- `409` — Conflict (duplicate)
- `422` — Unprocessable Entity
- `500` — Internal Server Error

## Request/Response Format

### JSON Structure
```typescript
// Success response
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}

// Error response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      { "field": "email", "message": "Must be a valid email" }
    ]
  }
}
```

### Pagination
```typescript
// Query params
GET /api/users?page=1&limit=20&sort=created_at:desc

// Response meta
{
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

## Authentication

- Use Bearer tokens in Authorization header
- Validate tokens on protected routes
- Return 401 for missing/invalid tokens

```typescript
// Request header
Authorization: Bearer <token>

// Middleware
if (!token || !validateToken(token)) {
  return res.status(401).json({
    success: false,
    error: { code: 'UNAUTHORIZED', message: 'Invalid token' }
  });
}
```

## Validation

- Validate request body with Zod or Joi
- Return specific validation errors
- Sanitize input before processing

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(['user', 'admin']).default('user'),
});

// In route handler
const result = CreateUserSchema.safeParse(req.body);
if (!result.success) {
  return res.status(400).json({
    success: false,
    error: {
      code: 'VALIDATION_ERROR',
      message: 'Invalid request data',
      details: result.error.issues
    }
  });
}
```

## Rate Limiting

- Apply rate limits to public endpoints
- Use sliding window or token bucket
- Return 429 with retry-after header

```typescript
// Response headers
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```
