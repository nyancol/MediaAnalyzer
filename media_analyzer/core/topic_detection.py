from configparser import ConfigParser
from nltk.corpus import stopwords
import spacy
from media_analyzer import database


def tokenize(text, parser, stop_words):
    tokens = [word.lemma_ for word in parser(text.lower()) if not word.like_url]
    return list(filter(lambda token: token not in stop_words, tokens))


def load_topics(language):
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT topic, keywords FROM topics WHERE language = '{language}'")
        rows = cur.fetchall()
        cur.close()
    topics = {}
    for topic, keywords in rows:
        topics[topic] = keywords
    return topics


def analyze(tokens, topics):
    matches = [False] * len(topics)
    for i, (topic, keywords) in enumerate(topics.items()):
        for token in tokens:
            if any([key == token for key in keywords]):
                matches[i] |= True
    return [t for t, m in zip(topics, matches) if m]


def update_topics(tweets):
    sql = "UPDATE tweets SET topics = %(topics)s WHERE id = %(id)s"
    with connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        conn.commit()
        cur.close()


def update():
    languages = database.get_languages()
    for language in languages:
        print(f"Updating {language}")
        tweets = database.load_tweets(language=language)
        topics = load_topics(language)
        for tweet in tweets:
            tweet["topics"] = analyze(tweet["tokens"], topics)
        print(f"Finished updating {language}")
        update_topics(tweets)


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
    pass
    # update()
