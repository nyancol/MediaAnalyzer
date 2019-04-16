import pika
from time import sleep
import contextlib
from media_analyzer import exceptions


@contextlib.contextmanager
def connection(rabbit_ip="localhost", retry=3):
    timeout = 30
    conn = None
    error = None
    while retry >= 0 and conn is None:
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(rabbit_ip))
        except pika.exceptions.AMQPConnectionError as err:
            retry -= 1
            error = err
            sleep(timeout)
    if conn is None:
        msg = "Failed when creating a connection to RabbitMQ"
        raise exceptions.RabbitMQException(msg) from error
    else:
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
