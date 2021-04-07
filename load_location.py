import logging
import time

from geopy import geocoders
from sqlalchemy.orm import sessionmaker
from tzwhere import tzwhere

from db import engine
from models import User

logger = logging.getLogger("LoadLocation")
logger.setLevel("INFO")
g = geocoders.Nominatim(user_agent="gh-collaborative-data", timeout=600)
logger.info("Geocoder is ready")
w = tzwhere.tzwhere(forceTZ=True)
session = sessionmaker(bind=engine)(autoflush=True)


def get_coordinates(locl: str):
    try:
        location = g.geocode(query=locl)
        logger.info(f"found ({location.latitude}, {location.longitude})")
        time.sleep(1)
        return location.latitude, location.longitude
    except AttributeError:
        logger.warning(f"Cannot find coordinates of '{user.location}'")
        return 0, 0


users = session.query(User).filter(User.utc_locale == None, User.location != None).all()
for user in users:
    logger.info(f"Searching for UTC locale for '{user.login}' from '{user.location}'")
    lat, lgn = get_coordinates(user.location)
    if not lat:
        continue
    utc_locale = w.tzNameAt(lat, lgn, forceTZ=True)
    if utc_locale:
        logger.info(f"UTC locale defined as {utc_locale}")
        user.utc_locale = utc_locale
        session.commit()
    else:
        logger.warning("could not find a UTC locale of the provided data. Skipping...")
