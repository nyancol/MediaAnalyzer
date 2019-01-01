from media_analyzer import database
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import spacy
spacy.load('fr')
from spacy.lang.fr import French


def update():
    languages = database.get_languages()
    for language in languages:
        print(f"Updating {language}")
        tweets = database.load_tweets(language=language)
        print(f"Updating {len(tweets)} tweets")
        tweets = run(tweets, language)
        database.update_sentiment(tweets)


def get_analyzer(language):
    if language == "english":
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores
    else:
        return lambda text: {"neg": 0, "neu": 0, "pos": 0, "compound": 0}


def run(tweets, language):
    analyzer = get_analyzer(language)
    for tweet in tweets:
        score = analyzer(tweet["text"])
        tweet["negative"] = score["neg"]
        tweet["neutral"] = score["neu"]
        tweet["positive"] = score["pos"]
    return tweets


if __name__ == "__main__":
    update()
