from configparser import ConfigParser
import tweepy

def get_twitter():
    config = ConfigParser()
    config.read("media_analyzer/api_keys.ini")
    consumer_key = config.get("twitter", "consumer_key")
    consumer_secret = config.get("twitter", "consumer_secret")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    return tweepy.API(auth)
