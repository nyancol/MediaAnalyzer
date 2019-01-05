import numpy as np
from datetime import datetime
from flask import Flask
from flask import Markup
from flask import Flask, request
from flask import render_template

from . import database

app = Flask(__name__)


def get_weekly_topic_stats(publisher=None, language=None):
    res = None
    conditions = []
    condition = ""
    if publisher:
        conditions.append(f"publisher = '{publisher}'")
    if language:
        conditions.append(f"language = '{language}'")
    if language or publisher:
        condition = " AND " + " AND ".join(conditions)

    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT topic FROM topics")
        topics = [t[0] for t in cur.fetchall()]
        begin = datetime(2018, 10, 1)
        cur.execute(f"""SELECT topics.topic, date_trunc('week', tweets.created_at::date) AS weekly, COUNT(*)
                            FROM tweets JOIN topics ON topics.topic = ANY(tweets.topics)
                            WHERE '{begin}'::date < tweets.created_at {condition}
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

def get_thirty_days_topics():
    res = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT begin, topics FROM thirty_days_topics WHERE language = 'english'")
        res = cur.fetchall()
        cur.close()
    # return [{"begin": begin, "topics": topics} for begin, topics in res]
    return [{"topics": topics} for _, topics in res]


@app.route("/")
def chart():
    language_selected = "english"
    # if request.args["language_selector"] != "all":
    #     language_selected = request.args["language_selector"]

    topics_stats = get_weekly_topic_stats(language=language_selected)
    languages = database.get_languages()
    thirty_days_stats = get_thirty_days_topics()
    print(thirty_days_stats[0])
    return render_template('chart.html', languages=languages, topics_stats=topics_stats,
                            thirty_days_stats=thirty_days_stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
