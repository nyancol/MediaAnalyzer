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
        conn = psycopg2.connect(**params)
        yield conn
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_tables():
    commands = [
    # """
    # CREATE TABLE tweets (
    #     id bigint PRIMARY KEY,
    #     publisher text REFERENCES publishers(screen_name),
    #     language text NOT NULL,
    #     created_at timestamp NOT NULL,
    #     text text NOT NULL,
    #     original_screen_name text NOT NULL,
    #     raw json NOT NULL
    # );
    # """,
    # """
    # CREATE TABLE topics (
    #     topic text NOT NULL,
    #     language text NOT NULL,
    #     keywords text[] NOT NULL,
    #     PRIMARY KEY (language, keywords)
    # );
    # """,
    # """
    # CREATE TABLE thirty_days_topics (
    #     begin date,
    #     language text,
    #     topics json,
    #     PRIMARY KEY (begin, language)
    # );
    # """,
    # """
    # CREATE TABLE publishers (
    #     screen_name text PRIMARY KEY,
    #     name text NOT NULL,
    #     country text,
    #     city text,
    #     description text,
    #     language text,
    #     profile_image_url text,
    #     insert_date timestamp
    # );
    # """
    ]

    with connection() as conn:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()


def drop_tables():
    tables = ["tweets", "topics", "thirty_days_topics",
              "publishers"]
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
        cur.execute("SELECT DISTINCT language FROM publishers;")
        rows = cur.fetchall()
        cur.close()
    return [row[0] for row in rows]


def get_topics():
    with connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT topic FROM topics;")
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


if __name__ == "__main__":
    pass
    # drop_tables()
    # create_tables()
