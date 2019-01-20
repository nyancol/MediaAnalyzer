import csv
import datetime
import tweepy
import json

from media_analyzer import database
from media_analyzer import apis
from . import sentiment_analysis
from . import topic_detection


def insert_tweets(tweets):
    for tweet in tweets:
        tweet["raw"] = json.dumps(tweet["raw"])

    sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                 tokens, topics, negative, neutral, positive, raw)
             VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                     %(text)s, %(tokens)s, %(topics)s, %(negative)s, %(neutral)s,
                     %(positive)s, %(raw)s);"""
    with database.connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        cur.close()
        conn.commit()


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
    for status in tweepy.Cursor(api.user_timeline, since_id=since_id, id=publisher).items():
        tweets.append({"id": status.id,
                       "publisher": publisher,
                       "created_at": status.created_at,
                       "text": status.text,
                       "raw": status._json})
    return tweets


def get_publishers(language):
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT screen_name
                        FROM publishers
                        WHERE language = '{language}';""")
        rows = cur.fetchall()
    return [row[0] for row in rows]


def main():
    api = apis.get_twitter()
    languages = database.get_languages()
    for language in languages:
        publishers = get_publishers(language)
        tweets = []
        for publisher in publishers:
            print("Pulling {:<20}".format(publisher), end=" - ")
            p_tweets = get_last_tweets(api, publisher)
            for p_tweet in p_tweets:
                p_tweet["language"] = language
            print(f"Found {len(p_tweets)} new tweets")
            tweets.extend(p_tweets)

        print("Analyzing topics")
        tweets = topic_detection.run(tweets, language)
        print("Analyzing sentiments")
        tweets = sentiment_analysis.run(tweets, language)
        insert_tweets(tweets)


if __name__ == "__main__":
    main()
