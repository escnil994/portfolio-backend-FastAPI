# Architecture Documentation

## Overview

Portfolio Backend is built using modern Python async patterns with FastAPI, following clean architecture principles and SOLID design patterns.

## Technology Stack

### Core Framework
- **FastAPI 0.120+** - Modern async web framework
- **Python 3.11+** - Latest Python features
- **Uvicorn** - ASGI server
- **Pydantic 2.0** - Data validation

### Database
- **SQLAlchemy 2.0** - Async ORM
- **SQL Server** - Primary database
- **Alembic** - Database migrations
- **aioodbc + pyodbc** - Async SQL Server driver

### Authentication
- **python-jose** - JWT tokens
- **bcrypt** - Password hashing
- **pyotp** - TOTP generation
- **Azure Communication Services** - Email 2FA

### Development
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Type checking
- **Docker** - Containerization

## Architecture Layers

```
┌─────────────────────────────────────────┐
│           API Layer (FastAPI)           │
│  /api/v1/endpoints/*.py                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer (Business)        │
│  /services/*.py                         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Repository Layer (Data Access)     │
│  /db/repositories/*.py                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Model Layer (Database)          │
│  /models/*.py                           │
└─────────────────────────────────────────┘
```

## Design Patterns

### Repository Pattern
Abstracts data access logic from business logic.

```python
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any):
        ...
    
    async def create(self, db: AsyncSession, obj_in):
        ...
```

### Service Pattern
Encapsulates business logic.

```python
class MediaService:
    async def add_image(self, db, entity_id, entity_type, ...):
        # Business logic here
        ...
```

### Dependency Injection
FastAPI's built-in DI for clean dependencies.

```python
async def get_current_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    ...
```

## Database Schema

### Users & Authentication
- `users` - User accounts
- `two_factor_codes` - 2FA codes
- `login_attempts` - Security tracking

### Content
- `profiles` - User profiles
- `projects` - Project showcase
- `blog_posts` - Blog content
- `comments` - User comments

### Media
- `images` - Polymorphic images (projects, blog, profiles)
- `videos` - Video content

### Engagement
- `reactions` - User reactions (like, love, etc.)
- `contact_messages` - Contact form submissions

## Key Features

### Polymorphic Associations
Images and reactions use polymorphic pattern:

```python
class Image:
    entity_id = Column(Integer)
    entity_type = Column(String)  # 'project', 'blog_post', 'profile'
```

### Async Operations
All database operations are async:

```python
async def get_projects(db: AsyncSession):
    result = await db.execute(select(Project))
    return result.scalars().all()
```

### Centralized Media Management
Single service handles all media operations:

```python
await media_service.add_image(db, entity_id, 'project', url)
await media_service.get_images(db, entity_id, 'project')
```

## Security

### Authentication Flow
1. User submits credentials
2. Credentials validated
3. 2FA code sent (if enabled)
4. User verifies 2FA
5. JWT token issued

### Authorization
- JWT tokens with expiration
- Role-based access (user/admin)
- Protected endpoints via dependencies

### Password Security
- bcrypt hashing
- Minimum 8 characters
- Login attempt tracking
- Account lockout after 5 failed attempts

## Performance Optimizations

### Database
- Connection pooling (10 connections, 20 overflow)
- Async queries
- Eager loading with `selectinload`
- Batch image loading to prevent N+1 queries

### Caching
- Redis integration ready
- Cache service abstraction

### Query Optimization
```python
# Load images for multiple entities at once
images_dict = await media_service.load_images_for_entities(
    db, [1, 2, 3], 'project'
)
```

## Error Handling

### Custom Exceptions
```python
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)
```

### Consistent Error Responses
All errors return JSON:
```json
{
  "detail": "Error message"
}
```

## Scalability

### Horizontal Scaling
- Stateless application
- JWT tokens (no session storage)
- External cache (Redis)

### Database Scaling
- Read replicas support ready
- Connection pooling
- Async operations

### Microservices Ready
- Service layer abstracts business logic
- Repository pattern for data access
- Easy to extract services

## Testing Strategy

### Unit Tests
- Repository layer tests
- Service layer tests
- Utility function tests

### Integration Tests
- API endpoint tests
- Authentication flow tests
- Database integration tests

### Test Database
SQLite for fast test execution:
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
```

## Deployment Architecture

```
┌──────────────┐
│   Nginx      │ ← Reverse Proxy
└──────────────┘
       ↓
┌──────────────┐
│   FastAPI    │ ← Application
│  (Uvicorn)   │
└──────────────┘
       ↓
┌──────────────┐
│  SQL Server  │ ← Database
└──────────────┘
```

## Monitoring & Logging

### Structured Logging
```python
logger.info(f"User {user_id} logged in")
logger.error(f"Failed to send email: {error}")
```

### Health Checks
```
GET /health
{
  "status": "healthy",
  "app": "Portfolio API",
  "version": "1.0.0"
}
```

## Future Enhancements

- [ ] GraphQL endpoint
- [ ] WebSocket support for real-time features
- [ ] Elasticsearch for full-text search
- [ ] Redis caching implementation
- [ ] Rate limiting middleware
- [ ] API versioning strategy
- [ ] Audit trail system