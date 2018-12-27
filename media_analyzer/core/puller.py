from media_analyzer import database
from . import sentiment_analysis
from . import topic_detection

from configparser import ConfigParser
import tweepy
import csv
import datetime

def get_api():
    config = ConfigParser()
    config.read("media_analyzer/api_keys.ini")
    consumer_key = config.get("twitter", "consumer_key")
    consumer_secret = config.get("twitter", "consumer_secret")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    return tweepy.API(auth)


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


def load_publishers():
    config = ConfigParser(allow_no_value=True)
    config.read("media_analyzer/core/publishers.ini")
    publishers = {}
    for s in config.sections():
        publishers[s] = config.options(s)
    return publishers


def main():
    api = get_api()
    publishers = load_publishers()
    for language in publishers:
        tweets = []
        for publisher in publishers[language]:
            print("Pulling {:<20}".format(publisher), end=" - ")
            t_tweets = get_tweets(api, publisher)
            for tweet in t_tweets:
                tweet["language"] = language
            print(f"Found {len(t_tweets)} new tweets")
            tweets.extend(t_tweets)
        print("Analyzing topics")
        tweets = topic_detection.run(tweets, language)
        print("Analyzing sentiments")
        tweets = sentiment_analysis.run(tweets, language)
        database.insert_tweet(tweets)


if __name__ == "__main__":
    main()
