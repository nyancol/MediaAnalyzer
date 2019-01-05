from configparser import ConfigParser
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
import spacy
from media_analyzer import database


def tokenize(text, parser, stop_words):
    tokens = [word.lemma_ for word in parser(text.lower()) if not word.like_url]
    return list(filter(lambda token: token not in stop_words, tokens))


def load_topics(language):
    config = ConfigParser(allow_no_value=True)
    config.read("media_analyzer/core/topics.ini")
    topics = {}
    for s in config.sections():
        topic_list = config.get(s, language)[1:-1]
        topics[s] = [t.strip() for t in topic_list.split(',')]
    return topics


def analyze(tokens, topics):
    def similarity(w1, w2):
        return 1 if w1 == w2 else 0

    matches = [False] * len(topics)
    threshold = 0.9
    for i, (topic, keywords) in enumerate(topics.items()):
        for token in tokens:
            if any([similarity(key, token) > threshold for key in keywords]):
                matches[i] |= True
    return [t for t, m in zip(topics, matches) if m]


def update():
    languages = database.get_languages()
    for language in languages:
        print(f"Updating {language}")
        tweets = database.load_tweets(language=language)
        tweets = run(tweets, language)
        print(f"Finished updating {language}")
        database.update_topics(tweets)


def get_parser(language):
    parsers = {
               "english": "en",
               "french": "fr",
               "spanish": "es",
               "italian": "it",
              }
    return spacy.load(parsers[language])


def run(tweets, language):
    topics = load_topics(language)
    parser = get_parser(language)
    stop_words = set(stopwords.words(language))

    for tweet in tweets:
        tweet["tokens"] = tokenize(tweet["text"], parser, stop_words)
        tweet["topics"] = analyze(tweet["tokens"], topics)
    return tweets


if __name__ == "__main__":
    update()
