import datetime
import numpy as np
import json
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import spacy
from media_analyzer import database


NUM_TOPICS = 20


def load_data(begin, end, language):
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT text, tokens
                        FROM tweets
                        WHERE language = '{language}'
                            AND '{begin}'::date < created_at
                            AND created_at < '{end}'::date;""")
        res = cur.fetchall()
    return [{"text": text, "tokens": tokens} for text, tokens in res]


def create_model(language, data):
    stop_words = stopwords.words(language)
    vectorizer = CountVectorizer(min_df=5, max_df=0.9, lowercase=True,
                                 stop_words=stop_words, token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')
    data_vectorized = vectorizer.fit_transform(data)

    # Build a Non-Negative Matrix Factorization Model
    nmf_model = NMF(n_components=NUM_TOPICS)
    nmf_Z = nmf_model.fit_transform(data_vectorized)
    return nmf_model, vectorizer.get_feature_names()


def get_top_topics(language, tweets):
    model, vocabulary = create_model(language, [tweet["text"] for tweet in tweets])
    components = []
    special_words = {"nhttps"}
    for topic in model.components_:
        keywords = [vocabulary[i] for i in np.argwhere(topic >= 1).flatten()]
        keywords = [key for key in keywords if key not in special_words]
        if keywords:
            components.append(keywords)
    return components


def get_last_date(language):
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT MAX(begin)
                        FROM thirty_days_topics
                        WHERE language = '{language}';""")
        res = cur.fetchone()
    return res[0] if res else None


def save_topics(begin, language, topics):
    sql = """INSERT INTO thirty_days_topics (begin, language, topics)
             VALUES (%(begin)s, %(language)s, %(topics)s);"""

    entry = {"begin": begin, "language": language, "topics": json.dumps(topics)}
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, entry)
        conn.commit()
        cur.close()


def get_date_fist_tweets():
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT MIN(created_at) FROM tweets;")
        res = cur.fetchone()
    return res[0]


def count_matches(tweets, topics, language):
    def count_matches_tweet(tokens, topics):
        topics = [set(keywords) for keywords in topics]
        topics_matched = np.zeros(len(topics), dtype=int)
        for i, keywords in enumerate(topics):
            if any([token in keywords for token in tokens]):
                topics_matched[i] = 1
        return topics_matched

    def get_tokens(language, topics):
        parsers = {"english": "en", "french": "fr",
                   "spanish": "es", "italian": "it"}
        parser = spacy.load(parsers[language])
        return [[parser(key)[0].lemma_ for key in keywords] for keywords in topics]

    tokenized_topics = get_tokens(language, topics)
    matches = np.zeros(len(topics), dtype=int)
    for tweet in tweets:
        matches += count_matches_tweet(tweet["tokens"], tokenized_topics)
    return [{"keywords": topic, "matches": match}
            for topic, match in zip(topics, matches.tolist())]


def compute_language(language):
    begin = get_last_date(language)
    if begin is None:
        begin = datetime.datetime(2018, 12, 1).date()
    else:
        begin += datetime.timedelta(days=1)

    while begin < datetime.datetime.now().date() - datetime.timedelta(days=30):
        end = begin + datetime.timedelta(days=30)
        print(f"Computing interval: {begin} -> {end} for {language}")
        tweets = load_data(begin, end, language)
        topics = get_top_topics(language, tweets)
        topics = count_matches(tweets, topics, language)
        save_topics(begin, language, topics)
        begin += datetime.timedelta(days=1)


def compute():
    languages = database.get_languages()
    for language in languages:
        compute_language(language)


if __name__ == "__main__":
    compute()
