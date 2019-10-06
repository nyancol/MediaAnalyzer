import argparse
import pickle
from uuid import uuid4
import io
import psycopg2.errors
from fastavro import writer, parse_schema
import json
from functools import partial
from datetime import datetime
from pathlib import Path

from media_analyzer import apis
from media_analyzer import queue


def upload(rabbit_ip="localhost", batch_size=100):
    records = []
    schema_file = Path(__file__).parent / "tweet.avsc"
    with open(schema_file) as f:
        raw_schema = json.load(f)
    schema = parse_schema(raw_schema)
    aws_resource = apis.get_aws()
    bucket = aws_resource.Bucket("media-analyzer-store")

    def upload_records(records):
        stream = io.BytesIO()
        writer(stream, schema, records)
        stream.seek(0)
        file_name = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4()) + ".avro"
        bucket.upload_fileobj(stream, file_name)

    def callback(chn, method, properties, body):
        record = pickle.loads(body)
        record["created_at"] = int(record["created_at"].timestamp())
        records.append(record)
        if len(records) >= batch_size:
            print(f"Inserting {len(records)} records")
            upload_records(records)
            records.clear()
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.queue_declare(queue="records_datalake", durable=True)
        channel.queue_bind("records_datalake", "records_router")
        channel.basic_consume(queue="records_datalake", on_message_callback=callback)
        channel.start_consuming()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP", required=True)
    parser.add_argument("--batch-size", help="Batch Size", default=100, type=int)
    args = parser.parse_args()
    upload(args.queue_ip, args.batch_size)


if __name__ == "__main__":
    main()
