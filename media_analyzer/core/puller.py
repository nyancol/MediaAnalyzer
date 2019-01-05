import csv
import datetime

from media_analyzer import database
from media_analyzer import apis
from . import sentiment_analysis
from . import topic_detection


def get_last_id(publisher):
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(id) FROM tweets WHERE publisher = '{publisher}';")
        since_id = cur.fetchone()
        cur.close()
    return since_id[0]


def get_tweets(api, publisher):
    tweets = []
    since_id = get_last_id(publisher)
    for status in tweepy.Cursor(api.user_timeline, since_id=since_id, id=publisher).items():
        tweets.append({"id": status.id,
                       "publisher": publisher,
                       "created_at": status.created_at,
                       "text": status.text})
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
            p_tweets = get_tweets(api, publisher)
            for p_tweet in p_tweets:
                p_tweet["language"] = language
            print(f"Found {len(p_tweets)} new tweets")
            tweets.extend(p_tweets)

        print("Analyzing topics")
        tweets = topic_detection.run(tweets, language)
        print("Analyzing sentiments")
        tweets = sentiment_analysis.run(tweets, language)
        database.insert_tweet(tweets)


if __name__ == "__main__":
    main()
