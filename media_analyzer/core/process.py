import json
import pickle
from media_analyzer import queue
from media_analyzer import database


### TODO: should it be moved to a Reddis DB? Overkill. Maybe reddis also for keeping MAX(ID). Partition tweets table on 'publishers'?
### TODO: Benchmark this query
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


def process_tweets():
    def callback(chn, method, properties, body):
        tweet = pickle.loads(body)
        record = process_tweet(tweet)
        chn.basic_ack(delivery_tag=method.delivery_tag)
        chn.basic_publish(exchange="", routing_key="records", body=pickle.dumps(record))

    with queue.connection() as conn:
        channel = conn.channel()
        channel.basic_consume(queue="tweets", on_message_callback=callback)
        channel.start_consuming()


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


if __name__ == "__main__":
    process_tweets()
