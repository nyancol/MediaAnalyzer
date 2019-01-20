import numpy as np
from datetime import datetime
from flask import Flask
from flask import Markup
from flask import Flask, request
from flask import render_template

from . import database
from .core import publishers
from . import apis

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


def run_query(query):
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        res = cur.fetchall()
    return res


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
    input_publisher = ""
    print(request.args)
    if "text" in request.args and request.args.get('text') != "":
        twitter_name = request.args.get("text")
        api = apis.get_twitter()
        input_publisher = publishers.get_info(api, twitter_name)
        for key in input_publisher:
            if input_publisher[key] is None or key == "insert_timestamp":
                input_publisher[key] = ""

    publishers_stats = publishers.get_publishers()
    for publisher in publishers_stats:
        for key in publisher:
            if publisher[key] is None or key == "insert_timestamp":
                publisher[key] = ""
    return render_template('publishers.html', publishers=publishers_stats, input_publisher=input_publisher)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
    # app.run(host="192.168.1.11", port=8080)
