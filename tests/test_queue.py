from time import sleep
from media_analyzer import queue
from media_analyzer import exceptions
import pytest


@pytest.fixture
def channel():
    with queue.connection() as conn:
        channel = conn.channel()
        channel.queue_declare(queue="test")
        yield channel
        channel.queue_delete(queue="test")


def test_queue_is_up():
    with queue.connection() as conn:
        pass
        

def test_queue_creation(channel):
    channel.basic_publish(exchange="", routing_key="test", body="asdf")


def test_queue_publish_consume(channel):
    def callback(chn, method, properties, body):
        chn.stop_consuming()
    channel.basic_publish(exchange="", routing_key="test", body="asdf")
    channel.basic_consume(queue="test", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def test_multiple_acks_consumer(channel):
    """Publish 10 messages but only ack up to 5th one"""
    def callback(chn, method, properties, body):
        if int(body) == 5:
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
            chn.stop_consuming()

    for i in range(10):
        channel.basic_publish(exchange="", routing_key="test", body=str(i+1))

    channel.basic_consume(queue="test", on_message_callback=callback)
    channel.start_consuming()

    res = channel.queue_declare(queue="test")
    remaining = res.method.message_count
    assert remaining == 5

def test_batch_consume(channel):
    records = []

    def callback(chn, method, properties, body):
        print(body)
        records.append(body)
        if len(records) >= 5:
            print("Got 5 records")
            ## TO PROCESSING HERE
            records.clear()
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        if int(body) == 19:
            chn.stop_consuming()

    for i in range(20):
        channel.basic_publish(exchange="", routing_key="test", body=str(i))

    channel.basic_consume(queue="test", on_message_callback=callback)
    channel.start_consuming()

    res = channel.queue_declare(queue="test")
    remaining = res.method.message_count
    assert remaining == 0
