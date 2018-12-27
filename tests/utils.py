import csv


def load_tweets(input_csv):
    tweets = []
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f,
                                delimiter=';',
                                escapechar='\\',
                                quoting=csv.QUOTE_NONE,
                                lineterminator='\n')
        for row in reader:
            tweets.append(row)
    return tweets

