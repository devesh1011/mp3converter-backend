# Notification Service

A microservice that sends email notifications when MP3 conversions are complete. Consumes messages from RabbitMQ and sends user emails.

## Features

- 📧 Email notifications for MP3 conversion completion
- 📨 Consumes messages from RabbitMQ queue
- 🔄 Async message processing
- ✉️ SMTP email integration
- 🔐 Secure credential management

## How It Works

1. **Message Consumption**: Listens to `mp3` queue on RabbitMQ
2. **Message Parsing**: Extracts user information and MP3 file details
3. **Email Composition**: Creates notification email with download link
4. **Email Sending**: Sends email via SMTP server
5. **Acknowledgment**: Acknowledges message on success, nacks on failure

## Environment Variables

```env
RABBITMQ_HOST=rabbitmq                    # RabbitMQ hostname
MP3_QUEUE=mp3                             # Queue name to consume
SMTP_SERVER=smtp.gmail.com                # SMTP server address
SMTP_PORT=587                             # SMTP port
SMTP_USER=your_email@gmail.com            # Sender email
SMTP_PASSWORD=your_app_password           # SMTP password (app-specific)
```

## Message Format

**Input (from converter):**

```json
{
  "video_fid": "ObjectId_string",
  "mp3_fid": "ObjectId_string",
  "username": "user@example.com"
}
```

## Email Template

```
Subject: Your MP3 is Ready! 🎵

Hi [username],

Your video has been successfully converted to MP3!

📊 Details:
- Video ID: [video_fid]
- MP3 ID: [mp3_fid]
- Conversion Time: [timestamp]

Download your MP3:
[Download Link]

Best regards,
MP3 Converter Team
```

## Dependencies

- Python 3.12+
- pika (RabbitMQ client)
- smtplib (Python standard library)
- email (Python standard library)

## Running

**Docker:**

```bash
docker build -t notification:latest .
docker run --env-file .env notification:latest
```

**Local:**

```bash
python consumer.py
```

## SMTP Configuration

### Gmail Setup

1. Enable 2-Factor Authentication in Google Account
2. Generate App-Specific Password:
   - Go to myaccount.google.com → Security
   - Create 16-character app password
   - Use as `SMTP_PASSWORD`

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

### Other SMTP Providers

- **SendGrid**: smtp.sendgrid.net:587
- **AWS SES**: email-smtp.region.amazonaws.com:587
- **Office 365**: smtp.office365.com:587

## Error Handling

- **Message Parsing Error**: Logs error and nacks message
- **SMTP Connection Error**: Retries with exponential backoff
- **Email Send Failure**: Nacks message for retry
- **Invalid Email**: Logs warning and acknowledges message

## Architecture

```
RabbitMQ (mp3 queue)
         ↓
Notification Service
         ↓
  Parse Message
         ↓
  Generate Email
         ↓
  SMTP Server
         ↓
  User Email
```

## Monitoring

Monitor queue depth:

```bash
# Check pending messages
docker exec rabbitmq rabbitmqctl list_queues mp3
```

## Future Enhancements

- SMS notifications
- Push notifications
- Email templates with HTML
- Retry mechanisms for failed emails
- Email tracking (read receipts)
