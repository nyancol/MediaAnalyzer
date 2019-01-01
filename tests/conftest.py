import tests.utils


def tweets():
    input_csv = "tests/tweets.csv"
    return tests.utils.load_tweets(input_csv)
