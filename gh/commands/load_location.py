import logging
import time

from geopy import geocoders
from geopy.geocoders.base import Geocoder
from retry import retry
from rich.progress import track
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
        time.sleep(1)
        return location.latitude, location.longitude
    except AttributeError:
        logger.warning(f"Cannot find coordinates of '{user.location}'")
        return 0, 0


def load():
    g = geocoders.Nominatim(user_agent="gh-collaborative-data", timeout=600)
    logger.info("Geocoder is ready")
    w = tzwhere.tzwhere(forceTZ=True)
    session = sessionmaker(bind=engine)(autoflush=True)

    users = (
        session.query(User).filter(User.utc_locale == None, User.location != None).all()
    )

    for index in track(range(len(users)), description="Processing..."):
        user = users[index]
        logger.info(
            f"Searching for UTC locale for '{user.login}' from '{user.location}'"
        )
        lat, lgn = get_coordinates(g, user)
        if not lat:
            continue
        utc_locale = w.tzNameAt(lat, lgn, forceTZ=True)
        if utc_locale:
            logger.info(f"UTC locale defined as {utc_locale}")
            user.utc_locale = utc_locale
            session.commit()
        else:
            logger.warning(
                "could not find a UTC locale of the provided data. Skipping..."
            )
