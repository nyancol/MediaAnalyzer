from configparser import ConfigParser
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
import jellyfish
import spacy
import spacy.lang
from media_analyzer import database


def tokenize(text, parser):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


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
        tweets = database.load_tweets(language=language)
        tweets = run(tweets, language)
        database.update_topics(tweets)


def run(tweets, language):
    def get_parser(language):
        parsers = {
                   "english": "en",
                   "french": "fr",
                   "spanish": "es",
                  }
        spacy.load(parsers[language])
        return eval(f"spacy.lang.{parsers[language]}.{language.title()}")()

    def get_stemmer():
        return lambda word: SnowballStemmer(language).stem(word)

    def get_lemma_2(word):
        lemmatizer = WordNetLemmatizer()
        return lambda word: lemmatizer.lemmatize(word, pos='v')

    def get_lemma(word):
        lemma = wn.morphy(word)
        if lemma is None:
            return word
        else:
            return lemma

    topics = load_topics(language)
    parser = get_parser(language)
    stemmer = get_stemmer()
    stop_words = set(stopwords.words(language))

    for tweet in tweets:
        tokens = tokenize(tweet["text"], parser)
        tokens = filter(lambda token: token in stop_words, tokens)
        tokens = map(stemmer, tokens)
        tweet["topics"] = analyze(tokens, topics)
    return tweets


if __name__ == "__main__":
    update()
