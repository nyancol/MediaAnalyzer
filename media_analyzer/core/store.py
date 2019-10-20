import argparse
import json
import pickle
import psycopg2.errors
from fastavro import reader, parse_schema
from pathlib import Path
import io

from media_analyzer import database
from media_analyzer import queue
from media_analyzer import exceptions


def store(rabbit_ip="localhost", postgres_ip="localhost", batch_size=100):
    records = []

    schema_file = Path(__file__).parent / "tweet.avsc"
    with open(schema_file) as f:
        raw_schema = json.load(f)
    schema = parse_schema(raw_schema)

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
        stream = io.BytesIO(body)
        for tweet in reader(stream, schema):
            records.append(process_tweet(tweet, postgres_ip))
        stream.close()

        if len(records) >= batch_size:
            print(f"Inserting {len(records)} records")
            with database.connection(postgres_ip) as db_conn:
                insert_records(db_conn, records)
            records.clear()
            chn.basic_ack(delivery_tag=method.delivery_tag, multiple=True)

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.queue_declare(queue="records_db", durable=True)
        channel.queue_bind("records_db", "records_router")
        channel.basic_consume(queue="records_db", on_message_callback=callback)
        channel.start_consuming()

### TODO: should it be moved to a Reddis DB? Overkill. Maybe reddis also for keeping MAX(ID). Partition tweets table on 'publishers'?
### TODO: Benchmark this query
def get_language(publisher, host="localhost"):
    with database.connection(host) as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT language
                        FROM publishers
                        WHERE screen_name = '{publisher}';
                     """)
        language = cur.fetchone()[0]
        cur.close()
    return language



def process_tweet(tweet, postgres_ip="localhost"):
    record = {
             "id": tweet["id"],
             "created_at": tweet["created_at"],
             "text": tweet["text"],
             "raw": json.dumps(tweet),
             "publisher": tweet["user"]["screen_name"],
             "retweets": tweet["retweet_count"],
             "favorites": tweet["favorite_count"],
             "language": get_language(tweet["user"]["screen_name"], postgres_ip),
             "original_screen_name": None,
            }

    if "retweeted_status" in tweet:
        record["original_screen_name"] = tweet["retweeted_status"]["user"]["screen_name"]
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP", required=True)
    parser.add_argument("--postgres-ip", help="Postgresql IP", required=True)
    parser.add_argument("--batch-size", help="Batch Size", default=100, type=int)
    args = parser.parse_args()
    store(args.queue_ip, args.postgres_ip, args.batch_size)


if __name__ == "__main__":
    main()
