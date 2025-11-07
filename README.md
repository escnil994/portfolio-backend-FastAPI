# README.md

# Portfolio Backend API

Modern FastAPI backend for a professional portfolio website with blog, projects showcase, authentication, and reactions system.

## Features

- **Authentication & Authorization**: JWT-based auth with 2FA support (Email & TOTP)
- **Profile Management**: Personal profile with bio, skills, and social links
- **Projects Showcase**: CRUD operations with images, videos, and comments
- **Blog System**: Full-featured blog with slug-based URLs and rich content
- **Comments System**: Moderated comments on projects and blog posts
- **Reactions System**: Like, Love, and Congratulations reactions
- **Contact Form**: Email notifications with Azure Communication Services
- **Media Management**: Centralized image and video management

## Tech Stack

- **FastAPI** - Modern async web framework
- **Python 3.11+** - Latest Python features
- **SQLAlchemy 2.0** - Async ORM
- **SQL Server** - Database (via aioodbc + pyodbc)
- **Alembic** - Database migrations
- **Azure Communication Services** - Email delivery
- **JWT** - Secure authentication
- **Docker** - Containerization

## Prerequisites

- Python 3.11+
- SQL Server 2019+ or Azure SQL Database
- Azure Communication Services account
- ODBC Driver 18 for SQL Server

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd portfolio-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Migrations
```bash
alembic upgrade head
```

### 6. Create Admin User
```bash
python scripts/create_admin.py
```

### 7. Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## Docker Deployment

### Build and Run
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

## Project Structure
```
portfolio-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── db/               # Database layer
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
├── tests/                # Test suite
└── docs/                 # Documentation
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Install Dev Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## Environment Variables

Key environment variables:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key (min 32 chars)
- `ADMIN_EMAIL` - Admin user email
- `ADMIN_PASSWORD` - Admin user password
- `AZURE_COMMUNICATION_CONNECTION_STRING` - Azure Communication Services
- `FRONTEND_URL` - Frontend application URL

See `.env.example` for complete list.

## Security

- JWT tokens with configurable expiration
- 2FA via email and TOTP
- Password hashing with bcrypt
- Login attempt tracking
- Rate limiting ready
- CORS configured

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Author

Portfolio Backend - Professional FastAPI Application