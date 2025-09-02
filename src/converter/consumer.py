import pika
import os
import time
import sys
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def main():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/videos")
    mongo_mp3_uri = os.getenv("MONGO_MP3_URI", "mongodb://mongo:27017/mp3s")

    client_videos = MongoClient(mongo_uri)
    client_mp3s = MongoClient(mongo_mp3_uri)

    db_videos = client_videos.videos
    db_mp3s = client_mp3s.mp3s

    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))

    channel = connection.channel()

    def callback(ch, method, properties, body):
        print(f"Received message: {body}")
        result = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        print(f"Processing result: {result}")

        if isinstance(result, dict) and not result.get("success", False):
            print(f"Error: {result}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # Declare queue to ensure it exists
    channel.queue_declare(queue=os.getenv("VIDEO_QUEUE"), durable=True)
    channel.basic_consume(queue=os.getenv("VIDEO_QUEUE"), on_message_callback=callback)
    print("Waiting for messages! For exit Press CTRL + C.")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interuppted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
