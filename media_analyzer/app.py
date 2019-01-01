import numpy as np
from datetime import datetime
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template

# from configparser import ConfigParser
from . import database

app = Flask(__name__)


def get_weekly_topic_stats():
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT topic FROM topics")
        topics = [t[0] for t in cur.fetchall()]
        begin = datetime(2018, 10, 1)
        cur.execute(f"""SELECT topics.topic, date_trunc('week', tweets.created_at::date) AS weekly, COUNT(*)
                            FROM tweets JOIN topics ON topics.topic = ANY(tweets.topics)
                            WHERE '{begin}'::date < tweets.created_at 
                            GROUP BY weekly, topics.topic
                            ORDER BY weekly;""")
        res = cur.fetchall()
        cur.close()

    weeks = []
    weekly_stats = []
    topics = set([t for t, _, _ in res])
    weeks = list(set([w.strftime("%Y-%m-%d") for _, w, _ in res]))
    topics_stats = dict([(topic, np.zeros(len(weeks))) for topic in topics])
    i = 0
    j = 0
    while i < len(res):
        w0 = res[i][1]
        while i < len(res) and res[i][1] == w0:
            topics_stats[res[i][0]][j] = res[i][2]
            i += 1
        j += 1
    return {
            "labels": weeks,
            "datasets": [{"label": topic, "data": data.tolist()} for topic, data in topics_stats.items()]
           }


def get_language_stats():
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT language, COUNT(*) FROM tweets GROUP BY language")
        res = cur.fetchall()
        cur.close()
    languages, counts = zip(*res)
    return {"languages": list(languages), "counts": list(counts)}


def get_tweet_count():
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tweets")
        count = cur.fetchone()
        cur.close()
    return count[0]


@app.route("/")
def chart():
    topics_stats = get_weekly_topic_stats()
    languages_stats = get_language_stats()
    tweet_count = get_tweet_count()
    return render_template('chart.html', tweet_count=tweet_count, languages_stats=languages_stats, topics_stats=topics_stats)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
