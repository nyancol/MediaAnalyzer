import json
import argparse
import pickle
from media_analyzer import queue
from media_analyzer import database


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


def process_tweets(rabbit_ip="localhost", postgres_ip="localhost"):
    def callback(chn, method, properties, body):
        tweet = pickle.loads(body)
        record = process_tweet(tweet, postgres_ip)
        chn.basic_ack(delivery_tag=method.delivery_tag)
        chn.basic_publish(exchange="", routing_key="records", body=pickle.dumps(record))

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.queue_declare(queue="records", durable=True)
        channel.basic_consume(queue="tweets", on_message_callback=callback)
        channel.start_consuming()


def process_tweet(status, postgres_ip="localhost"):
    tweet = {
             "id": status.id,
             "created_at": status.created_at,
             "text": status.text,
             "raw": json.dumps(status._json),
             "publisher": status.user.screen_name,
             "retweets": status.retweet_count,
             "favorites": status.favorite_count,
             "language": get_language(status.user.screen_name, postgres_ip),
             "original_screen_name": None,
            }

    if hasattr(status, "retweeted_status"):
        tweet["original_screen_name"] = status.retweeted_status.user.screen_name
    return tweet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP")
    parser.add_argument("--postgres-ip", help="Postgresql IP")
    args = parser.parse_args()
    process_tweets(args.queue_ip, args.postgres_ip)


if __name__ == "__main__":
    main()
