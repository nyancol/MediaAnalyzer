import tweepy
import json
import fastavro
import io
import uuid

from media_analyzer import database
from media_analyzer import apis


#### PULL TWEETS ####
def get_publishers():
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT screen_name FROM publishers;")
        rows = cur.fetchall()
    return [row[0] for row in rows]


def get_last_id(publisher):
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(id) FROM tweets WHERE publisher = '{publisher}';")
        since_id = cur.fetchone()
        cur.close()
    return since_id[0]


def get_last_tweets(api, publisher):
    tweets = []
    since_id = get_last_id(publisher)
    return tweepy.Cursor(api.user_timeline, since_id=since_id, id=publisher).items()


def pull():
    api = apis.get_twitter()
    # Staging Tweets - Could be published to a Kafka topic with key: (language, publisher)
    # TODO: move to `tweets` array append to kafka producer
    raw_tweets = []
    for publisher in get_publishers():
        print("Pulling {:<20}".format(publisher), end=" - ")
        statii = get_last_tweets(api, publisher)
        raw_tweets.extend(statii)
    return raw_tweets


#### PROCESS TWEETS ####
def get_language(publisher):
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT language
                        FROM publishers
                        WHERE screen_name = '{publisher}';
                     """)
        language = cur.fetchone()[0]
        cur.close()
    return language


def process_tweet(status):
    tweet = {
             "id": status.id,
             "created_at": status.created_at,
             "text": status.text,
             "raw": json.dumps(status._json),
             "publisher": status.user.screen_name,
             "language": get_language(status.user.screen_name),
             "original_screen_name": None,
            }

    if hasattr(status, "retweeted_status"):
        tweet["original_screen_name"] = status.retweeted_status.user.screen_name
    return tweet


#### STORE PROCESSED TWEETS ####
def insert_tweets(tweets):
    sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                 original_screen_name, raw)
             VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                     %(text)s, %(original_screen_name)s, %(raw)s);"""
    with database.connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        cur.close()
        conn.commit()


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


#### MAIN ####
def main():
    raw_tweets = pull()

    # Process Tweets - Consume messages from Kafka
    # TODO: Should produce a message in another Kafka topic for each tweet processed
    records = []
    for raw_tweet in raw_tweets:
        records.append(process_tweet(raw_tweet))
        # upload_avro(tweets)
    insert_tweets(records)


if __name__ == "__main__":
    main()
