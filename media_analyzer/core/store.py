import argparse
import pickle
import uuid
import io
import fastavro
import psycopg2.errors

from media_analyzer import database
from media_analyzer import apis
from media_analyzer import queue
from media_analyzer import exceptions


def store_records(rabbit_ip="localhost", postgres_ip="localhost", batch_size=100):
    records = []

    def insert_records(db_conn, records):
        # except exceptions.DuplicateDBEntryException as err:
        sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                     original_screen_name, raw, retweets, favorites)
                 VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                         %(text)s, %(original_screen_name)s, %(raw)s, %(retweets)s, %(favorites)s);"""
        cur = db_conn.cursor()
        for record in records:
            try:
                cur.execute(sql, record)
            except psycopg2.errors.UniqueViolation as err:
                db_conn.rollback()
        cur.close()
        db_conn.commit()

    def callback(chn, method, properties, body):
        record = pickle.loads(body)
        records.append(record)
        if len(records) >= batch_size:
            print(f"Inserting {len(records)} records")
            with database.connection(postgres_ip) as db_conn:
                insert_records(db_conn, records)
            records.clear()
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.basic_consume(queue="records", on_message_callback=callback)
        channel.start_consuming()


def upload_avro(records):
    schema = {
        "doc": "Tweets pulled and enriched",
        "name": "Media Analyzer",
        "namespace": "com.media_analyzer.v1.tweets",
        "type": "record",
        "fields": [
            {"name": "id", "type": "long"},
            {"name": "publisher", "type": "string"},
            {"name": "language", "type": "string"},
            {"name": "created_at", "type": "int", "logicalType": "time-millis"},
            {"name": "text", "type": "string"},
            {"name": "tokens", "type": "array", "items": "string"},
            {"name": "raw", "type": "string"},
        ]
    }
    schema = fastavro.parse_schema(schema)
    bytes_array = io.BytesIO()
    fastavro.writer(bytes_array, schema, tweets)

    resource = apis.get_aws()
    bucket = "media-analyzer-store"
    file_name = str(uuid.uuid4().hex[:6]) + ".avro"
    resource.upload_fileobj(bytes_array, bucket_name=bucket, key=file_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP", required=True)
    parser.add_argument("--postgres-ip", help="Postgresql IP", required=True)
    parser.add_argument("--batch-size", help="Batch Size", default=100, type=int)
    args = parser.parse_args()
    store_records(args.queue_ip, args.postgres_ip, args.batch_size)


if __name__ == "__main__":
    main()
