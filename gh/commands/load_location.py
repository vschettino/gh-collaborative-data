import logging
import time

import requests
from geopy import geocoders
from geopy.geocoders.base import Geocoder
from retry import retry
from rich.progress import track
from shapely.geometry import Point, mapping, shape
from shapely.prepared import prep
from sqlalchemy.orm import sessionmaker
from tzwhere import tzwhere

from gh.db import engine
from gh.models import User

logger = logging.getLogger("LoadLocation")


@retry(backoff=1.1, delay=120, max_delay=600)
def get_coordinates(g: Geocoder, user: User):
    try:
        location = g.geocode(query=user.location)
        logger.info(f"found ({location.latitude}, {location.longitude})")
        return location.latitude, location.longitude
    except AttributeError:
        logger.warning(f"Cannot find coordinates of '{user.location}'")
        return 0, 0


def get_countries() -> dict:
    data = requests.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    ).json()

    countries = {}
    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ISO_A2"]
        countries[country] = prep(shape(geom))
    logger.info(f"Loaded {len(countries)} from 'geo-countries'")
    return countries


def get_country(countries, lat, lon):
    point = Point(lon, lat)
    for country, geom in countries.items():
        if geom.contains(point):
            return country


def load(*args, **kwargs):
    g = geocoders.Nominatim(user_agent="gh-collaborative-data", timeout=600)
    logger.info("Geocoder is ready")
    w = tzwhere.tzwhere(forceTZ=True)
    session = sessionmaker(bind=engine)(autoflush=True)
    countries = get_countries()
    users = (
        session.query(User)
        .filter(User.location != None and User.latitude != None)
        .all()
    )
    count_users = len(users)
    logger.info(f"Ready to get location of '{count_users}' users")
    for index in track(range(count_users), description="Processing..."):
        user = users[index]
        logger.info(
            f"Searching for UTC locale for '{user.login}' from '{user.location}'"
        )
        lat, lgn = get_coordinates(g, user)
        if not lat:
            continue
        user.latitude = lat
        user.longitude = lgn
        utc_locale = w.tzNameAt(lat, lgn, forceTZ=True)
        if utc_locale:
            logger.info(f"UTC locale defined as {utc_locale}")
            user.utc_locale = utc_locale
        else:
            logger.warning(
                "could not find a UTC locale of the provided data. Skipping..."
            )
            continue
        country = get_country(countries, lat, lgn)
        if country:
            logger.info(f"country defined as '{country}'")
            user.country = country
        else:
            logger.warning(f"No country found using ({lat}, {lgn}) ")
        session.commit()
