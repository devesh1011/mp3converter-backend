import pika
import os
import sys
from send import email


def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))

    channel = connection.channel()

    def callback(ch, method, properties, body):
        print(f"Received message: {body}")
        err = email.notification(body)

        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.queue_declare(queue=os.getenv("MP3_QUEUE"), durable=True)
    channel.basic_consume(queue=os.getenv("MP3_QUEUE"), on_message_callback=callback)
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
