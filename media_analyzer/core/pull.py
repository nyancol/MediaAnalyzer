import argparse
import pickle
import tweepy
from tweepy.error import TweepError
from time import sleep
import datetime

from media_analyzer import database
from media_analyzer import apis
from media_analyzer import queue


def get_last_id(publisher, host="localhost"):
    with database.connection(host) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(id) FROM tweets WHERE publisher = '{publisher}';")
        since_id = cur.fetchone()
        cur.close()
    return since_id[0]


def get_last_tweets(api, publisher, postgres_ip="localhost"):
    since_id = get_last_id(publisher, postgres_ip)
    return tweepy.Cursor(api.user_timeline, since_id=since_id, id=publisher).items()


def pull_tweets(rabbit_ip="localhost", postgres_ip="localhost"):
    def callback(chn, method, properties, body):
        publisher = body.decode("utf-8")
        api = apis.get_twitter()
        print(f"Publishing a tweets for {publisher}")
        statii = get_last_tweets(api, publisher, postgres_ip)
        now = datetime.datetime.utcnow()
        try:
            for status in statii:
                if now - datetime.timedelta(hours=24) < status.created_at:
                    continue
                chn.basic_publish(exchange="", routing_key="tweets", body=pickle.dumps(status))
        except tweepy.error.TweepError as err:
            # In case reaches maximum number of requests, sleep for 15 min and retry
            sleep(15 * 60)
            return callback(chn, method, properties, body)
        chn.basic_ack(delivery_tag=method.delivery_tag)

    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.queue_declare(queue="tweets", durable=True)
        channel.basic_consume(queue="publishers", on_message_callback=callback)
        channel.start_consuming()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP")
    parser.add_argument("--postgres-ip", help="Postgresql IP")
    args = parser.parse_args()
    pull_tweets(args.queue_ip, args.postgres_ip)


if __name__ == "__main__":
    main()
