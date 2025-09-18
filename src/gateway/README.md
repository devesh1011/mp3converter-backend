# Gateway Service

Central API gateway for the microservices architecture. Handles file uploads, downloads, and routes requests to other services. Manages authentication via JWT tokens.

## Features

- 🚪 API Gateway with request routing
- 📤 File upload to MongoDB GridFS
- 📥 MP3 streaming download
- 🔐 JWT authentication validation
- 📨 Async message publishing to RabbitMQ
- 🔀 Service-to-service proxy (auth, etc.)

## Architecture

```
User/Client
     ↓
  Nginx (Reverse Proxy)
     ↓
Gateway Service
     ├→ Auth Service (validate tokens)
     ├→ MongoDB (store/retrieve files)
     └→ RabbitMQ (publish messages)
```

## API Endpoints

### 1. **Login** (Pass-through to Auth Service)

```
POST /login
Content-Type: application/json

Body:
{
  "username": "alice123",
  "password": "securepass456"
}

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### 2. **Upload Video**

````
POST /upload

## Environment Variables

```env
# Auth Service
AUTH_SERVICE_HOST=auth
AUTH_SERVICE_PORT=8001

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
VIDEO_QUEUE=video                          # Queue for videos
VIDEO_EXCHANGE=video_exchange

# MongoDB - Videos
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=videos_db
MONGO_COLLECTION=videos

# MongoDB - MP3s
MONGO_MP3_HOST=mongo
MONGO_MP3_PORT=27017
MONGO_MP3_DB=mp3_db
MONGO_MP3_COLLECTION=mp3_files
````

Or use connection URIs:

```env
MONGO_URI=mongodb://mongo:27017/videos_db
MONGO_MP3_URI=mongodb://mongo:27017/mp3_db
```

## Dependencies

```python
fastapi >= 0.119.0
uvicorn >= 0.30.0
pymongo >= 4.0
pika >= 1.3.0
python-jose >= 3.3.0
fastapi-jwt-bearer >= 0.1.0
```

## Running

**Docker:**

```bash
docker build -t gateway:latest .
docker run \
  -e AUTH_SERVICE_HOST=auth \
  -e RABBITMQ_HOST=rabbitmq \
  -e MONGO_URI=mongodb://mongo:27017/videos_db \
  -p 8002:8002 \
  gateway:latest
```

**Local:**

```bash
python server.py
```

Service starts on `http://localhost:8002`

## Testing with curl

**Register:**

```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

**Login:**

```bash
curl -X POST http://localhost:8002/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice123","password":"securepass456"}' \
  | jq '.access_token'
```

**Upload:**

```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8002/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample.mp4"
```

**Download:**

```bash
TOKEN="your_token_here"
FILE_ID="693d2c346cee6edba5e0ad6d"

curl -X GET "http://localhost:8002/download/$FILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  --output downloaded.mp3
```

## Request/Response Flow

### Upload Flow

```
Client Request
     ↓
JWT Validation (auth service)
     ↓
Store in GridFS (mongo)
     ↓
Publish to RabbitMQ
     ↓
Return file_id
     ↓
Client receives file_id
```

### Download Flow

```
Client Request (with file_id)
     ↓
JWT Validation
     ↓
Retrieve from GridFS (mp3 collection)
     ↓
Stream response (StreamingResponse)
     ↓
Client receives MP3 file
```

## Error Handling

| Status | Meaning                              |
| ------ | ------------------------------------ |
| 200    | Success                              |
| 400    | Bad request (invalid file format)    |
| 401    | Unauthorized (invalid/missing token) |
| 404    | File not found (invalid file_id)     |
| 422    | Validation error                     |
| 500    | Server error                         |

## File Size Limits

- Maximum upload size: 500MB (configurable)
- Recommended: 50-200MB for fast processing

## Performance Optimization

- **Streaming Downloads**: Large files streamed instead of loaded to memory
- **Lazy RabbitMQ Connection**: Connection created only when needed
- **MongoDB Indexing**: Indexes on file_id for fast retrieval
- **Connection Pooling**: Reuse MongoDB and RabbitMQ connections

## Kubernetes Deployment

See [gateway-deploy.yml](manifests/gateway-deploy.yml) for K8s configuration.

```bash
kubectl apply -f manifests/
kubectl port-forward svc/gateway 8002:8002
```

## Security Considerations

- ✅ JWT token validation on all file operations
- ✅ HTTPS in production (via nginx reverse proxy)
- ✅ Environment variables for secrets (no hardcoding)
- ⚠️ Add rate limiting for upload endpoint
- ⚠️ Validate file types (mime type checking)
- ⚠️ Implement request size limits
- ⚠️ Add API key for service-to-service auth

## Future Enhancements

- Rate limiting per user
- File size validation
- Virus scanning on upload
- Conversion progress tracking
- Batch file upload
- File retention policies
- Audit logging

## Security

- JWT token-based authentication
- Token expiration (1 hour default)
- HTTPS recommended for production
- File validation before upload
