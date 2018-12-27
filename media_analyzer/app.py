import datetime
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template

from . import database

app = Flask(__name__)


def count_topic(begin, end):
    topic = "islam"
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT COUNT(*)
                        FROM tweets
                        WHERE '{topic}' = ANY (topics)
                            AND '{begin}'::date < created_at
                            AND created_at < '{end}'::date;""")
        count = cur.fetchone()[0]
        cur.close()
    print(f"Found {count} matches for {topic} between {begin} and {end}")
    return count
    

@app.route("/")
def chart():
    week_delta = datetime.timedelta(days=7)
    weeks = sorted([datetime.datetime.now() - i * week_delta for i in range(10)])
    labels = [week.strftime("%Y-%m-%d") for week in weeks]
    # labels = ["January","February","March","April","May","June","July","August"]
    # values = [10,9,8,7,6,4,7,8]
    values = [count_topic(begin, end) for begin, end in zip(weeks, weeks[1:])]
    return render_template('chart.html', values=values, labels=labels)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
