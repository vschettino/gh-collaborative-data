import logging

import pandas
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from gh.db import engine
from gh.models import Interaction, Repository

logger = logging.getLogger("Interactions")


def general_interactions(*args, **kwargs):
    session = sessionmaker(bind=engine)()
    interactions_per_week = (
        session.query(
            func.date_trunc("week", Interaction.created_at).label("created_at"),
            Interaction.type,
            Repository.full_name.label("project"),
            func.count("*").label("total"),
        )
        .join(Repository)
        .group_by(text("1,2,3"))
    )
    df = pandas.read_sql(interactions_per_week.statement, session.bind)
    logger.info(df.head())
