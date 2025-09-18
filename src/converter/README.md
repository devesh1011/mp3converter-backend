# Video to MP3 Converter Service

A microservice that converts video files to MP3 audio files using RabbitMQ message queue and MoviePy.

## Features

- 🎬 Converts video files to MP3 format
- 📨 Consumes messages from RabbitMQ queue
- 🗄️ Stores videos in MongoDB GridFS
- 📤 Publishes converted MP3s to notification queue
- 🔄 Async processing with message acknowledgment

## How It Works

1. **Message Consumption**: Listens to `video` queue on RabbitMQ
2. **Video Retrieval**: Downloads video from MongoDB GridFS using video ID
3. **Audio Extraction**: Uses MoviePy to extract audio from video
4. **MP3 Storage**: Saves converted MP3 to MongoDB GridFS (mp3s collection)
5. **Message Publishing**: Publishes conversion result to `mp3` queue for notifications
6. **Acknowledgment**: Acknowledges message when successful, nacks on error

## Environment Variables

```env
RABBITMQ_HOST=rabbitmq          # RabbitMQ hostname
VIDEO_QUEUE=video               # Input queue name
MP3_QUEUE=mp3                   # Output queue name
MONGO_URI=mongodb://mongo:27017/videos   # Video database URI
MONGO_MP3_URI=mongodb://mongo:27017/mp3s # MP3 database URI
```

## Message Format

**Input (from gateway):**

```json
{
  "video_fid": "ObjectId_string",
  "mp3_fid": null,
  "username": "user@example.com"
}
```

**Output (to notification):**

```json
{
  "video_fid": "ObjectId_string",
  "mp3_fid": "ObjectId_string",
  "username": "user@example.com"
}
```

## Dependencies

- Python 3.12
- pika (RabbitMQ client)
- pymongo (MongoDB driver)
- moviepy (video processing)
- ffmpeg (audio/video processing)

## Running

**Docker:**

```bash
docker build -t converter:latest .
docker run --env-file .env converter:latest
```

**Local:**

```bash
python consumer.py
```

## Architecture

```
RabbitMQ (video queue)
         ↓
  Converter Service
         ↓
  Extract Audio (MoviePy + FFmpeg)
         ↓
  Store MP3 (MongoDB GridFS)
         ↓
  Publish to mp3 queue
         ↓
  Notification Service
```
