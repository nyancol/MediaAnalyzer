import pytest
from  media_analyzer.core import topic_detection
from nltk.corpus import stopwords


text = ["BREAKING: Federal appeals court rules against Trump administration on DACA https://t.co/KHnrNvEKAM"]

tokens = [["break", ":", "federal", "appeal", "court", "rule", "against", "trump", "administration", "on", "daca", "https://t.co/khnrnvekam"]]

clean_tokens = [["break", ":", "federal", "appeal", "court", "rule", "trump", "administration", "daca", "https://t.co/khnrnvekam"]]


@pytest.mark.parametrize("text,expected_tokens", zip(text, tokens))
def test_tokens(text, expected_tokens):
    parser = topic_detection.get_parser("english")
    tokens = topic_detection.tokenize(text, parser)
    assert tokens == expected_tokens


@pytest.mark.parametrize("tokens, expected_clean_tokens", zip(tokens, clean_tokens))
def test_clean_tokens(tokens, expected_clean_tokens):
    stop_words = set(stopwords.words("english"))
    clean_tokens = topic_detection.clean_tokens(tokens, stop_words)
    assert clean_tokens == expected_clean_tokens
