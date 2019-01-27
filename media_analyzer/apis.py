from configparser import ConfigParser
import tweepy
import boto3

def get_twitter():
    config = ConfigParser()
    config.read("media_analyzer/api_keys.ini")
    consumer_key = config.get("twitter", "consumer_key")
    consumer_secret = config.get("twitter", "consumer_secret")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    return tweepy.API(auth)

def get_aws():
    config = ConfigParser()
    config.read("media_analyzer/api_keys.ini")
    access_key = config.get("aws", "access_key")
    secret_key = config.get("aws", "secret_key")
    resource = boto3.resource('s3', aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)
    return resource
