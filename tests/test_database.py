import media_analyzer.database as database


def test_load_tweets():
    tweets = database.load_tweets()
    assert len(tweets) > 1000
    assert type(tweets) == list
    assert type(tweets[0]) == dict


def test_load_tweets_publisher():
    tweets = database.load_tweets(publisher="nytimes")
    assert len(tweets) > 1000
    assert all([tweet["publisher"] == "nytimes" for tweet in tweets])


def test_load_tweets_language():
    tweets = database.load_tweets(language="french")
    assert len(tweets) > 1000
    assert all([tweet["language"] == "french" for tweet in tweets])


def test_load_tweets_language_publisher():
    tweets = database.load_tweets(language="french", publisher="le_figaro")
    assert len(tweets) > 1000
    assert all([tweet["language"] == "french" for tweet in tweets])
    assert all([tweet["publisher"] == "le_figaro" for tweet in tweets])
