from media_analyzer import database
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def analyze(text):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)


def update():
    languages = database.get_languages()
    for language in languages:
        tweets = database.load_tweets(language=language)
        tweets = run(tweets, language)
        database.update_sentiment(tweets)


def run(tweets, language):
    for tweet in tweets:
        score = analyze(tweet["text"])
        tweet["negative"] = score["neg"]
        tweet["neutral"] = score["neu"]
        tweet["positive"] = score["pos"]
    return tweets


if __name__ == "__main__":
    update()
