import pika
import contextlib
from media_analyzer import exceptions


@contextlib.contextmanager
def connection():
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    except pika.exceptions.AMQPConnectionError as err:
        msg = "Failed when creating a connection to RabbitMQ"
        raise exceptions.RabbitMQException(msg) from err

    yield conn
    conn.close()


def init_queues():
    with connection() as conn:
        channel = conn.channel()
        channel.queue_declare(queue="tweets", durable=True)
        channel.queue_declare(queue="records", durable=True)
        channel.queue_declare(queue="publishers", durable=True)


def delete_queues():
    with connection() as conn:
        channel = conn.channel()
        channel.queue_delete(queue="tweets")
        channel.queue_delete(queue="records")
        channel.queue_delete(queue="publishers")


if __name__ == "__main__":
    delete_queues()
    init_queues()
