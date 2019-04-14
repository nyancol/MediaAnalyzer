from configparser import ConfigParser
from pathlib import Path
from functools import wraps
import tweepy
import boto3


def readconfig(f):
    """
    Calls the decorated function with the section of the configuration file
    (api_keys.ini) which is retrieved from the function name.
    The function must be named: <prefix>_<section_in_config>
    """
    @wraps(f)
    def wrapper():
        section = f.__name__.split('_')[1]
        config = ConfigParser()
        config_file = Path(__file__).parent / "api_keys.ini"
        config.read(config_file.as_posix())
        options = config.options(section)
        return f(dict({(option, config.get(section, option)) for option in options}))
    return wrapper


@readconfig
def get_twitter(config):
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    return tweepy.API(auth)


@readconfig
def get_aws(config):
    resource = boto3.resource('s3', aws_access_key_id=config["access_key"],
                              aws_secret_access_key=config["secret_key"])
    return resource


@readconfig
def get_newsapi(config):
    return config["key"]
