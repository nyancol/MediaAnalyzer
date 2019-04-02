import pickle
import uuid
import io
import fastavro

from media_analyzer import database
from media_analyzer import apis


def store_records():
    BATCH_SIZE = 100
    records = []

    def insert_records(records):
        sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                     original_screen_name, raw)
                 VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                         %(text)s, %(original_screen_name)s, %(raw)s);"""
        with database.connection() as conn:
            cur = conn.cursor()
            cur.executemany(sql, records)
            cur.close()
            conn.commit()

    def callback(chn, method, properties, body):
        record = pickle.loads(body)
        records.append(record)
        if len(records) >= BATCH_SIZE:
            print(f"Inserting {len(records)} records")
            insert_records(records)
            records.clear()
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)

    with queue.connection() as conn:
        channel = conn.channel()
        channel.basic_consume(queue="records", on_message_callback=callback)
        channel.start_consuming()


def upload_avro(tweets):
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


def finish_store():
    def insert_records(records):
        sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                     original_screen_name, raw)
                 VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                         %(text)s, %(original_screen_name)s, %(raw)s);"""
        print(f"Inserting {len(records)} processed tweets")
        with database.connection() as conn:
            cur = conn.cursor()
            cur.executemany(sql, records)
            cur.close()
            conn.commit()

    def callback(chn, method, properties, body):
        record = pickle.loads(body)
        insert_records([record])
        chn.basic_ack(delivery_tag=method.delivery_tag)

    with queue.connection() as conn:
        channel = conn.channel()
        channel.basic_consume(queue="records", on_message_callback=callback)
        channel.start_consuming()


if __name__ == "__main__":
    store_records()
