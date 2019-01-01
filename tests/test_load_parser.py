import spacy.lang
import timeit
import tests.utils


def multiple_load_parser():
    def get_parser(language):
        parsers = {
                   "english": "en",
                   "french": "fr",
                  }
        spacy.load(parsers[language])
        return eval(f"spacy.lang.{parsers[language]}.{language.title()}")()

    def tokenize(text, language):
        lda_tokens = []
        parser = get_parser(language)
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

    input_csv = "tests/tweets.csv"
    tweets = tests.utils.load_tweets(input_csv)[:100]
    for tweet in tweets:
        tokenize(tweet["text"], tweet["language"])


def single_load_parser():
    def get_parser(language):
        parsers = {
                   "english": "en",
                   "french": "fr",
                  }
        spacy.load(parsers[language])
        return eval(f"spacy.lang.{parsers[language]}.{language.title()}")()

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

    input_csv = "tests/tweets.csv"
    tweets = tests.utils.load_tweets(input_csv)[:100]
    parser = get_parser(tweets[0]["language"])
    for tweet in tweets:
        tokenize(tweet["text"], parser)


if __name__ == "__main__":
    print(timeit.timeit(single_load_parser, number=1))
    print(timeit.timeit(multiple_load_parser, number=1))
