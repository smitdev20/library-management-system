# Library Management System

A Django REST Framework-based library management system where users can search for books, and borrow them.

## 🚀 Live Demo

**Production API:** https://library-management-api-production-f85f.up.railway.app

- **Swagger UI:** https://library-management-api-production-f85f.up.railway.app/swagger/
- **API Documentation:** https://library-management-api-production-f85f.up.railway.app/redoc/
- **Admin Panel:** https://library-management-api-production-f85f.up.railway.app/admin/



## Features

- **User Authentication**: JWT-based authentication with registration, login, and token refresh
- **Role-Based Access Control**: Using Django Groups (Administrators, Members)
- **Book Management**: Browse, search, filter, and paginate books
- **Fuzzy Search**: PostgreSQL trigram + full-text search (handles typos)
- **Loan System**: Borrow and return books with availability tracking
- **Admin Panel**: Full Django admin for managing books and users
- **API Documentation**: Swagger/OpenAPI documentation
- **Security**: Protection against CSRF, XSS, SQL Injection

### Extra Features

- **Book Reviews & Ratings**: Users can rate and review books (demonstrates advanced DRF m2m relationships)
- **Advanced Fuzzy Search**: PostgreSQL trigram similarity for typo-tolerant search
- **Comprehensive Testing**: Unit + Integration tests with high coverage

## Technology Stack

- **Django 4.2+** - Web framework
- **Django REST Framework** - REST API
- **PostgreSQL** - Database (with pg_trgm for fuzzy search)
- **JWT Authentication** - djangorestframework-simplejwt
- **API Documentation** - drf-yasg (Swagger)
- **Docker** - Containerization
- **Railway** - Deployment platform
- **Docker** - Containerization

## User Roles

| Role | Permissions |
|------|-------------|
| Anonymous | Browse books (read-only) |
| Members | Browse books, borrow/return books, write reviews |
| Administrators | Full CRUD on books, manage users, view all loans |

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or Docker)
- pip

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-management-django
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run with Docker (recommended)**
   ```bash
   docker-compose up --build
   ```
   The API will be available at: http://localhost:8001

6. **Or run locally** (requires PostgreSQL)
   ```bash
   # Create database
   createdb library_django_db

   # Run migrations
   python manage.py migrate

   # Set up user groups
   python manage.py setup_groups

   # Create superuser
   python manage.py createsuperuser

   # Run server
   python manage.py runserver 8001
   ```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user |

### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List books (with search, filter, pagination) |
| GET | `/api/books/?search=query` | Search books (fuzzy matching) |
| GET | `/api/books/{id}/` | Get book details |
| POST | `/api/books/` | Create book (Admin only) |
| PUT | `/api/books/{id}/` | Update book (Admin only) |
| DELETE | `/api/books/{id}/` | Delete book (Admin only) |

### Loans

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/api/loans/borrow/` | `{"book_id": 1}` | Borrow a book |
| POST | `/api/loans/{id}/return_book/` | - | Return a book |
| GET | `/api/loans/` | - | List your loans |
| GET | `/api/loans/active/` | - | List active loans |
| GET | `/api/loans/my_loans/` | - | All loan history |
| GET | `/api/loans/overdue/` | - | Overdue loans (Admin only) |

### Reviews

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| GET | `/api/reviews/` | - | List reviews |
| POST | `/api/reviews/` | `{"book_id": 1, "rating": 5}` | Create review |
| GET | `/api/reviews/my_reviews/` | - | Your reviews |

## API Documentation

- **Swagger UI**: http://localhost:8001/swagger/
- **ReDoc**: http://localhost:8001/redoc/
- **Admin Panel**: http://localhost:8001/admin/

## Authentication

All protected endpoints require JWT authentication:

1. Login via `POST /api/auth/login/`
2. Copy the `access` token from response
3. Add header: `Authorization: <token>` (Bearer prefix optional)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=term-missing

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

**Test Coverage:**
- Unit tests for models (User, Book, Loan, Review)
- Integration tests for all API endpoints
- RBAC permission tests

## Deployment

This project is configured for deployment on **Railway** with PostgreSQL.

### Railway (Primary Platform)

**Quick Deploy via CLI:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
cd library-management-system
railway init

# Add PostgreSQL
railway add --database postgresql

# Set environment variables
railway variables set DEBUG=False
railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
railway variables set ALLOWED_HOSTS=.railway.app
railway variables set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy
railway up

# Get your deployment URL
railway domain
```

📖 **See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions**

### Docker

```bash
docker build -t library-management .
docker run -p 8001:8001 library-management
```

## Project Structure

```
library-management-django/
├── config/                 # Project configuration
│   ├── settings/
│   │   ├── base.py        # Common settings
│   │   ├── development.py # Dev settings (PostgreSQL)
│   │   ├── production.py  # Prod settings (Render/Heroku)
│   │   └── testing.py     # Test settings (SQLite)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User management & JWT auth
│   ├── books/             # Book management & search
│   ├── loans/             # Borrowing system
│   └── reviews/           # Book reviews
├── tests/
│   ├── unit/              # Model tests
│   └── integration/       # API endpoint tests
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
└── manage.py
```

## Security Features

- JWT token authentication with expiry
- CORS configuration
- CSRF protection
- XSS protection headers
- SQL injection prevention (Django ORM)
- HTTPS redirect in production
- Secure cookie settings

## License

MIT License
