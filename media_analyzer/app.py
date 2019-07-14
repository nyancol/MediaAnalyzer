import numpy as np
from datetime import datetime
import time
from flask import Flask
from flask import Markup
from flask import Flask, request
from flask import render_template

from . import database
from .core import publishers
from . import apis
from . import exceptions

app = Flask(__name__)


def get_weekly_topic_stats(language, topic):
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        begin = datetime(2018, 10, 1)
        cur.execute(f"""SELECT date_trunc('week', created_at::date) AS week,
                           COUNT(*), AVG(negative) AS avg_negative, AVG(neutral) AS avg_neutral,
                           AVG(positive) AS avg_positive
                        FROM tweets
                        WHERE '{begin}'::date < created_at
                            AND '{language}' = language
                            AND '{topic}' = ANY(topics)
                        GROUP BY week
                        ORDER BY week;""")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
    rows = [dict(zip(colnames, row)) for row in rows]
    for row in rows:
        row["week"] = row["week"].strftime("%Y-%m-%d")
    return rows


def get_thirty_days_topics(language):
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT begin, topics FROM thirty_days_topics WHERE language = '{language}'")
        res = cur.fetchall()
        cur.close()
    # return [{"begin": begin, "topics": topics} for begin, topics in res]
    return [{"topics": topics} for _, topics in res]


@app.route("/")
def chart():
    languages = database.get_languages()
    topics = database.get_topics()
    topics_stats = {}
    thirty_days_stats = {}
    for language in languages:
        topics_stats[language] = {}
        for topic in topics:
            topics_stats[language][topic] = get_weekly_topic_stats(language, topic)
        thirty_days_stats[language] = get_thirty_days_topics(language)
    return render_template('index.html', thirty_days_stats=thirty_days_stats)
    # return render_template('chart.html', languages=languages, topics_stats=topics_stats,
    #                         thirty_days_stats=thirty_days_stats, topics=topics)


def get_weekly_count(token):
    rows = None
    begin = datetime(2018, 10, 1)
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT date_trunc('week', created_at::date) AS week,
                            COUNT(*)
                        FROM tweets
                        WHERE '{token}' = ANY(tokens) AND '{begin}'::date < created_at
                        GROUP BY week
                        ORDER BY week;""")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
    rows = [dict(zip(colnames, row)) for row in rows]
    for row in rows:
        row["week"] = row["week"].strftime("%Y-%m-%d")
    return rows


@app.route('/search_engine')
def search_engine():
    tokens = []
    if "text" in request.args:
        text = request.args.get('text')
        tokens = [token.strip() for token in text.lower().split(',')]
    weekly_count = {}
    for token in tokens:
        weekly_count[token] = get_weekly_count(token)
    return render_template('search_engine.html', tokens_weekly_count=weekly_count, tokens=tokens)


def get_token_evolution(token):
    totals_view = """
            CREATE VIEW totals AS
                SELECT publisher, date_trunc('month', created_at) AS month, COUNT(*)
                FROM tweets
                GROUP BY publisher, month
            """
    tokens_view = """
            CREATE MATERIALIZED VIEW tokenized_tweets AS
                SELECT publishers.name AS publisher, date_trunc('month', created_at) AS month,
                       to_tsvector('simple', unaccent(text)) AS tokens
                FROM tweets
                    JOIN publishers ON tweets.publisher = publishers.screen_name
            WITH DATA
        """
    # tokens_view = """
    #         CREATE MATERIALIZED VIEW tokenized_tweets AS
    #             SELECT publishers.name AS publisher, date_trunc('month', created_at) AS month,
    #                    to_tsvector(publishers.language::regconfig, unaccent(text)) AS tokens
    #             FROM tweets
    #                 JOIN publishers ON tweets.publisher = publishers.screen_name
    #         WITH DATA
    #     """
    query = f"""
           SELECT publisher, COUNT(*) AS matches, month
           FROM tokenized_tweets
           WHERE tokens @@ to_tsquery('{token}')
           GROUP by publisher, month
           ORDER BY publisher, month
        """
    # query = f"""
    #     SELECT totals.month, totals.publisher,
    #            CASE WHEN matching.count is NULL THEN 0 ELSE matching.count END AS matches, totals.count AS total
    #     FROM (SELECT publisher, COUNT(*), month
    #           FROM tokenized_tweets
    #           WHERE tokens @@ to_tsquery('{token}')
    #           GROUP by publisher, month) as matching
    #         RIGHT OUTER JOIN totals ON matching.publisher = totals.publisher and matching.month = totals.month
    #     ORDER BY totals.publisher, totals.month
    # """
    # query = f"""
    #          SELECT total.month, total.publisher,
    #                 CASE WHEN matching.count is NULL THEN 0 ELSE matching.count END AS matches,
    #                 total.count AS total
    #          FROM (SELECT publisher, count(*), date_trunc('month', created_at) AS month
    #                FROM tweets JOIN publishers ON tweets.publisher = publishers.screen_name
    #                WHERE to_tsvector(publishers.language::regconfig, unaccent(text)) @@ to_tsquery('{token}')
    #                GROUP BY publisher, month) AS matching
    #          RIGHT OUTER JOIN (SELECT publisher, date_trunc('month', created_at) AS month, COUNT(*)
    #                            FROM tweets
    #                            GROUP BY publisher, month) AS total
    #          ON matching.publisher = total.publisher AND matching.month = total.month
    #          ORDER BY total.publisher, total.month
    #          """
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
    data = [dict(zip(colnames, row)) for row in rows]
    for i, record in enumerate(data):
        data[i]["month"] = record["month"].strftime('%Y-%m')
    return data


@app.route("/token_evolution", methods=["GET"])
def token_evolution():
    data = None
    query = None
    if "token" in request.args:
        query = request.args["token"]
        data = get_token_evolution(request.args["token"])
        # data = [{"month": datetime(2018, 11, 1).strftime('%Y-%m'), "publisher": "a", "matches": 23, "total": 20},{"month": datetime(2018, 12, 1).strftime('%Y-%m'), "publisher": "a", "matches": 22, "total": 20},
        #         {"month": datetime(2018, 10, 1).strftime('%Y-%m'), "publisher": "b", "matches": 4, "total": 20}, {"month": datetime(2018, 11, 1).strftime('%Y-%m'), "publisher": "b", "matches": 1, "total": 20}]
    return render_template('token_evolution.html', data=data, query=query)


def run_query(query):
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        res = cur.fetchall()
    return render_template('db_stats.html', query_text=query_response)


@app.route('/db_stats')
def db_stats():
    tokens = []
    query_response = ""
    if "text" in request.args and request.args.get('text') != "":
        query = request.args.get('text')
        query_response = run_query(query)
        if query_response is not None:
            query_response = [', '.join([str(item) for item in row]) for row in query_response]
            query_response = '<br>'.join(query_response)
    return render_template('db_stats.html', query_text=query_response)


@app.route('/publishers')
def publishers_route():
    print(request.args)
    message = None
    languages = database.get_languages()
    if ("screen_name" in request.args and request.args.get("screen_name") != "") \
            and ("language" in request.args):
        language = request.args.get("language").lower()
        if language not in languages:
            message = f"'{language}' not in {database.get_languages()}"
        else:
            twitter_name = request.args.get("screen_name")
            api = apis.get_twitter()
            try:
                publisher = publishers.get_info(api, twitter_name)
            except exceptions.InvalidTwitterUserException as exc:
                message = f"Twitter user '{twitter_name}' not found"
            else:
                try:
                    publishers.insert_db([publisher])
                    message = f"Added {publisher['name']} - {publisher['screen_name']} into DB"
                except exceptions.DuplicateDBEntryException:
                    message = f"{publisher['name']} is already present in DB"

    publishers_stats = publishers.get_publishers()
    for publisher in publishers_stats:
        for key in publisher:
            if publisher[key] is None or key == "insert_timestamp":
                publisher[key] = ""
    return render_template('publishers.html', publishers=publishers_stats, message=message,
                           language_pattern='|'.join(languages))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
    # app.run(host="192.168.1.237", port=8080)
    # app.run(host="192.168.1.11", port=8080)
