import argparse

from media_analyzer import database
from media_analyzer import queue


def select_publishers(rabbit_ip="localhost", postgres_ip="localhost"):
    rows = None
    with database.connection(postgres_ip) as conn:
        cur = conn.cursor()
        cur.execute("SELECT screen_name FROM publishers;")
        rows = cur.fetchall()
    publishers = [row[0] for row in rows if row[0] not in ["FoxNews", "foxnewspolitics"]]
    with queue.connection(rabbit_ip) as conn:
        channel = conn.channel()
        channel.queue_declare(queue="publishers", durable=True)
        for publisher in publishers:
            print(f"Publishing publisher: {publisher}")
            channel.basic_publish(exchange="", routing_key="publishers", body=publisher)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-ip", help="Rabbitmq IP")
    parser.add_argument("--postgres-ip", help="Postgresql IP")
    args = parser.parse_args()
    select_publishers(args.queue_ip, args.postgres_ip)


if __name__ == "__main__":
    main()
