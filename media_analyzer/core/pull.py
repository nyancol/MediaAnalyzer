import pickle
import tweepy

from media_analyzer import database
from media_analyzer import apis
from media_analyzer import queue


def select_publishers():
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT screen_name FROM publishers;")
        rows = cur.fetchall()
    publishers = [row[0] for row in rows][20:]
    with queue.connection() as conn:
        channel = conn.channel()
        for publisher in publishers:
            print(f"Publishing publisher: {publisher}")
            channel.basic_publish(exchange="", routing_key="publishers", body=publisher)


def get_last_id(publisher):
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(id) FROM tweets WHERE publisher = '{publisher}';")
        since_id = cur.fetchone()
        cur.close()
    return since_id[0]


def get_last_tweets(api, publisher):
    since_id = get_last_id(publisher)
    return tweepy.Cursor(api.user_timeline, since_id=since_id, id=publisher).items()


def pull_tweets():
    def callback(chn, method, properties, body):
        publisher = body.decode("utf-8")
        api = apis.get_twitter()
        print(f"Publishing a tweets for {publisher}")
        statii = get_last_tweets(api, publisher)
        for status in statii:
            chn.basic_publish(exchange="", routing_key="tweets", body=pickle.dumps(status))
        chn.basic_ack(delivery_tag=method.delivery_tag)

    with queue.connection() as conn:
        channel = conn.channel()
        channel.basic_consume(queue="publishers", on_message_callback=callback)
        channel.start_consuming()


def main():
    select_publishers()
    pull_tweets()


if __name__ == "__main__":
    main()
