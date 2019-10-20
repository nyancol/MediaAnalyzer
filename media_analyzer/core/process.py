import json
import argparse
import pickle
import io
from pathlib import Path
from fastavro import writer, parse_schema
from media_analyzer import queue
from media_analyzer import database


def process_tweets(rabbit_ip="localhost"):
    schema_file = Path(__file__).parent / "tweet.avsc"
    with open(schema_file) as f:
        raw_schema = json.load(f)
    schema = parse_schema(raw_schema)

    def callback(chn, method, properties, body):
        tweet = pickle.loads(body)
        stream = io.BytesIO()
        writer(stream, schema, [tweet._json])
        chn.basic_publish(exchange="records_router", routing_key="records", body=stream.getvalue())
        chn.basic_ack(delivery_tag=method.delivery_tag)

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.exchange_declare("records_router", exchange_type="fanout", durable=True)
        channel.queue_declare(queue="records")
        channel.basic_consume(queue="tweets", on_message_callback=callback)
        channel.start_consuming()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP")
    args = parser.parse_args()
    process_tweets(args.queue_ip)


if __name__ == "__main__":
    main()
