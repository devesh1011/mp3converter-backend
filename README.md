# MP3 Converter Backend

A microservices-based video-to-MP3 conversion system with authentication, file management, and async processing.

## Overview

This project converts uploaded video files (MP4) to MP3 audio files using a distributed microservices architecture. It features:

- User authentication with JWT tokens
- Video file uploads via API Gateway
- Async video-to-MP3 conversion using message queues
- Email notifications on conversion completion
- MongoDB GridFS for scalable file storage
- Kubernetes-ready deployment manifests

## Architecture

```
┌─────────────────┐
│   Client/User   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Nginx   │ (Reverse Proxy)
    └────┬────┘
         │
    ┌────▼─────────────────────────────────┐
    │     Gateway Service (Port 8002)      │
    │  - Upload/Download Management        │
    │  - Request Routing & Auth Validation │
    └────┬──────┬──────────┬───────────────┘
         │      │          │
    ┌────▼──┐ ┌─▼──────┐ ┌─▼──────────┐
    │ Auth  │ │MongoDB │ │  RabbitMQ  │
    │Svc    │ │GridFS  │ │ (Message Q)│
    │Port   │ │        │ └─┬───┬──────┘
    │8001   │ └────────┘   │   │
    └───────┘             ┌─▼─┐│
                          │   ││
                    ┌─────▼─┐││
                    │Converter││
                    │Service ││
                    │(Consumer)│
                    │- Convert ││
                    │  MP4→MP3 │
                    └──────────┘
                          │
                    ┌─────▼──────────┐
                    │ Notification   │
                    │ Service        │
                    │ (Email Alerts) │
                    └────────────────┘
```

## Services

### 1. **Authentication Service** (`src/auth/`)

- FastAPI + PostgreSQL
- User registration & login
- JWT token generation & validation
- Basic Auth support
- Password hashing with bcrypt

### 2. **Gateway Service** (`src/gateway/`)

- Central API endpoint for clients
- File upload to MongoDB GridFS
- MP3 download streaming
- JWT token validation
- RabbitMQ message publishing for conversion jobs

### 3. **Converter Service** (`src/converter/`)

- RabbitMQ message consumer
- Video-to-MP3 conversion (MoviePy)
- Stores converted files in MongoDB GridFS
- Publishes conversion completion events

### 4. **Notification Service** (`src/notification/`)

- RabbitMQ message consumer
- Email notifications on MP3 completion
- User notification handling

### 5. **Supporting Services**

- **PostgreSQL**: User database
- **MongoDB**: File storage (GridFS)
- **RabbitMQ**: Async message queue
- **Nginx**: Reverse proxy & load balancing

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- RabbitMQ
- PostgreSQL
- MongoDB

### Local Development

```bash
# Start all services
docker-compose up --build

# Services will be available at:
# - Gateway: http://localhost:8002
# - Auth: http://localhost:8001
# - RabbitMQ UI: http://localhost:15672
# - MongoDB: mongodb://localhost:27017
# - PostgreSQL: postgresql://localhost:5432
```

## API Endpoints

### Authentication

```bash
# Register
POST /register
{
  "name": "John Doe",
  "username": "johndoe",
  "password": "password123"
}

# Login
POST /login
Authorization: Basic <base64(username:password)>
```

### File Management

```bash
# Upload Video
POST /upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
file: <video_file.mp4>

# Download MP3
GET /download?fid=<file_id>
Authorization: Bearer <token>
```

## Kubernetes Deployment

Manifests are provided in each service's `manifests/` directory:

- StatefulSet for RabbitMQ
- Deployments for each microservice
- ConfigMaps & Secrets for configuration
- Services & Ingress for networking

```bash
# Deploy to Kubernetes
kubectl apply -f src/auth/manifests/
kubectl apply -f src/gateway/manifests/
kubectl apply -f src/converter/manifests/
kubectl apply -f src/notification/manifests/
kubectl apply -f src/rabbit/manifests/
```

## Environment Variables

See each service's `Dockerfile` and `docker-compose.yml` for required env vars:

- `JWT_SECRET`: JWT signing key
- `DATABASE_URL`: PostgreSQL connection string
- `MONGO_URI`: MongoDB URI for video storage
- `MONGO_MP3_URI`: MongoDB URI for MP3 storage
- `AUTH_SVC_ADDR`: Auth service address
- `VIDEO_QUEUE`: RabbitMQ video conversion queue
- `MP3_QUEUE`: RabbitMQ notification queue

## Project Structure

```
├── src/
│   ├── auth/              # Authentication service
│   ├── gateway/           # API Gateway
│   ├── converter/         # Video→MP3 converter
│   ├── notification/      # Email notifications
│   └── rabbit/            # RabbitMQ manifests
├── nginx/                 # Reverse proxy config
├── docker-compose.yml     # Local development setup
└── README.md
```

## Key Technologies

- **Backend**: FastAPI, Python 3.9+
- **Databases**: PostgreSQL (users), MongoDB (files)
- **Message Queue**: RabbitMQ
- **File Processing**: MoviePy (video conversion)
- **Containerization**: Docker, Kubernetes
- **Authentication**: JWT, Basic Auth
