from datetime import datetime
from configparser import ConfigParser
from geopy.geocoders import Nominatim
import tweepy.error
import psycopg2

from media_analyzer import database
from media_analyzer import apis
from media_analyzer import exceptions


def load_publishers():
    config = ConfigParser(allow_no_value=True)
    config.read("media_analyzer/core/publishers.ini")
    publishers = []
    for s in config.sections():
        publishers.extend(config.options(s))
    return publishers


def insert_db(publishers):
    for publisher in publishers:
        publisher["insert_timestamp"] = datetime.now()

    sql = """INSERT INTO publishers (screen_name, name, country,
                                     city, description, language,
                                     profile_image_url, insert_timestamp)
             VALUES (%(screen_name)s, %(name)s, %(country)s,
                     %(city)s, %(description)s, %(language)s,
                     %(profile_image_url)s, %(insert_timestamp)s);"""
    with database.connection() as conn:
        cur = conn.cursor()
        try:
            cur.executemany(sql, publishers)
        except psycopg2.IntegrityError as exc:
            conn.rollback()
            raise exceptions.DuplicateDBEntryException() from exc
        else:
            conn.commit()
        cur.close()


def get_info(api, publisher):
    user = None
    try:
        user = api.get_user(publisher)
    except tweepy.error.TweepError as err:
        raise exceptions.InvalidTwitterUserException() from err

    languages = {"en": "english", "it": "italian", "es": "spanish", "fr": "french"}

    country = None
    city = None
    if user.location:
        # Getting Option[Country], Option[City]
        geolocator = Nominatim(user_agent="media_analyzer")
        location = geolocator.geocode(user.location, language="en")
        if location is not None:
            location = location.raw
            location_name = location["display_name"]
            coords = "{},{}".format(location["lat"], location["lon"])
            full_location = geolocator.reverse(coords, language="en").raw["address"]
            country = full_location["country"]
            if "city" in full_location and full_location["city"] in location_name:
                city = full_location["city"]

    return {"screen_name": user.screen_name,
            "name": user.name,
            "country": country,
            "city": city,
            "description": user.description,
            "language": languages[user.lang],
            "profile_image_url": user.profile_image_url}


def get_publishers():
    rows = None
    with database.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM publishers ORDER BY language;")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
    return [dict(zip(colnames, row)) for row in rows]


def main():
    publishers = load_publishers()
    api = apis.get_twitter()
    inserted_publishers = set(get_publishers())
    publishers = [publisher for publisher in publishers
                  if publisher.lower() not in inserted_publishers]
    publishers = [get_info(api, publisher) for publisher in publishers]
    insert_db(publishers)


if __name__ == "__main__":
    main()
