# Authentication Service

A secure JWT-based authentication microservice built with FastAPI and PostgreSQL.

## Features

- ✅ User registration with password hashing (bcrypt)
- ✅ User login with Basic Auth
- ✅ JWT token generation and validation
- ✅ Secure password storage
- ✅ Token expiration (1 hour)
- ✅ PostgreSQL database integration

## API Endpoints

### Register User

```bash
POST /register
Content-Type: application/json

{
  "name": "John Doe",
  "username": "johndoe",
  "password": "secure_password"
}

Response: 201 Created
{
  "id": 1,
  "username": "johndoe",
  "name": "John Doe"
}
```

### Login

```bash
POST /login
Authorization: Basic base64(username:password)

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Validate Token

```bash
POST /validate
Authorization: Bearer <access_token>

Response: 200 OK
{
  "username": "johndoe",
  "valid": true
}
```

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres"
export JWT_SECRET="your-secret-key"

# Run migrations
python -m alembic upgrade head

# Start server
uvicorn server:app --reload --port 8001
```

### Docker

```bash
docker build -t auth-service .
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://postgres:password@db:5432/postgres" \
  -e JWT_SECRET="your-secret-key" \
  auth-service
```

## Environment Variables

| Variable       | Description                  | Default     |
| -------------- | ---------------------------- | ----------- |
| `DATABASE_URL` | PostgreSQL connection string | Required    |
| `JWT_SECRET`   | Secret key for JWT signing   | "secret"    |
| `DB_HOST`      | Database host                | "localhost" |
| `DB_USER`      | Database user                | "postgres"  |
| `DB_PASSWORD`  | Database password            | "password"  |
| `DB_NAME`      | Database name                | "postgres"  |

## Database Schema

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  username VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLModel** - SQL models
- **Passlib** - Password hashing
- **python-jose** - JWT handling
- **psycopg2** - PostgreSQL driver

## Testing

```bash
# Register a new user
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","username":"alice","password":"password123"}'

# Login
curl -X POST http://localhost:8001/login \
  -H "Authorization: Basic $(echo -n 'alice:password123' | base64)"

# Validate token
curl -X POST http://localhost:8001/validate \
  -H "Authorization: Bearer <access_token>"
```

## Security Notes

- Passwords are hashed using bcrypt with 10 rounds
- JWT tokens expire after 1 hour
- Always use HTTPS in production
- Store JWT_SECRET in environment variables, never in code
- Never log or expose passwords

## License

MIT
