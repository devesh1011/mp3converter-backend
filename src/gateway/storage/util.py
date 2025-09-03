import pika
import json


def upload(f, fs, channel, access):
    try:
        file_obj = f.file if hasattr(f, "file") else f
        fid = fs.put(file_obj)
    except Exception as err:
        raise RuntimeError(f"Failed to store file: {err}")

    message = {"video_fid": str(fid), "mp3_fid": None, "username": access["username"]}

    try:
        channel.queue_declare(queue="video", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        return {"status": "ok", "video_fid": str(fid)}

    except Exception as err:
        fs.delete(fid)
        raise RuntimeError(f"RabbitMQ publish failed: {err}")
