import contextlib
from configparser import ConfigParser
import psycopg2


def config(filename='media_analyzer/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


@contextlib.contextmanager
def connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        # print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        yield conn
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            # print('Database connection closed.')


def create_tables():
    commands = [
    # """
    # CREATE TABLE tweets (
    #     id bigint PRIMARY KEY,
    #     publisher varchar (25) NOT NULL,
    #     language varchar (20) NOT NULL,
    #     created_at timestamp NOT NULL,
    #     text varchar (300) NOT NULL,
    #     topics varchar[],
    #     negative float NOT NULL, 
    #     neutral float NOT NULL, 
    #     positive float NOT NULL
    # );
    # """,
    """
    CREATE TABLE topics (
        topic varchar (25) PRIMARY KEY
    );
    """,
    ]

    with connection() as conn:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()


def populate_tables():
    config = ConfigParser()
    config.read("media_analyzer/core/topics.ini")
    topics = [{"topic": topic} for topic in config.sections()]
    sql = """INSERT INTO topics (topic) VALUES (%(topic)s);"""
    with connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, topics)
        cur.close()
        conn.commit()


def drop_tables():
    tables = ["tweets", "topics"]
    with connection() as conn:
        cur = conn.cursor()
        for table in tables:
            cur.execute(f"DROP TABLE {table}")
        cur.close()
        conn.commit()


def get_publishers():
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT publisher FROM tweets;")
        rows = cur.fetchall()
        cur.close()
    return [row[0] for row in rows]


def get_languages():
    with connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT language FROM tweets;")
        rows = cur.fetchall()
        cur.close()
    return [row[0] for row in rows]


def load_tweets(publisher=None, language=None):
    with connection() as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM tweets"
        conditions = []
        if publisher:
            conditions.append(f"publisher = '{publisher}'")
        if language:
            conditions.append(f"language = '{language}'")

        if publisher or language:
            cur.execute(f"{sql} WHERE {' AND '.join(conditions)};")
        else:
            cur.execute(f"{sql};")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
    return [dict(zip(colnames, row)) for row in rows]


def insert_tweet(tweets):
    sql = """INSERT INTO tweets (id, publisher, language, created_at, text,
                                 topics, negative, neutral, positive)
             VALUES (%(id)s, %(publisher)s, %(language)s, %(created_at)s,
                     %(text)s, %(topics)s, %(negative)s, %(neutral)s, %(positive)s);"""
    with connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        cur.close()
        conn.commit()


def update_topics(tweets):
    sql = "UPDATE tweets SET topics = %(topics)s WHERE id = %(id)s"
    with connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        conn.commit()
        cur.close()


def update_sentiment(tweets):
    sql = """UPDATE tweets
             SET negative = %(negative)s, neutral = %(neutral)s, positive = %(positive)s
             WHERE id = %(id)s"""
    with connection() as conn:
        cur = conn.cursor()
        cur.executemany(sql, tweets)
        conn.commit()
        cur.close()


if __name__ == "__main__":
    drop_tables()
    create_tables()
    populate_tables()
