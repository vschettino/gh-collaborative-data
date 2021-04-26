import csv
import logging
from datetime import date
from statistics import mean, stdev
from typing import Dict, List

from scipy.stats import mannwhitneyu
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from gh.db import engine
from gh.models import Interaction, Repository, User

logger = logging.getLogger("Interactions")

REPOS = [
    (2081289, "astropy/astropy"),
    (4164482, "django/django"),
    (10270250, "facebook/react"),
    (23096959, "golang/go"),
    (20580498, "kubernetes/kubernetes"),
    (45717250, "tensorflow/tensorflow"),
]
OUTBREAK = date(2019, 11, 3)
session = sessionmaker(bind=engine)()

interactions_per_week = (
    session.query(
        func.date_trunc("week", Interaction.created_at).label("created_at"),
        func.count("*").label("total"),
    )
    .join(Repository)
    .group_by(text("1"))
)

weekend_interactions_per_week = (
    session.query(
        func.date_trunc(
            "week", Interaction.created_at.op("AT TIME ZONE")(User.utc_locale)
        ).label("created_at"),
        func.count("*").op("filter")(
            text(
                "(where extract(isodow from interactions.created_at AT TIME ZONE utc_locale) IN (1, 2))::float"
            )
            / func.count("*")
        ),
    )
    .join(User)
    .filter(User.utc_locale != "uninhabited")
    .group_by(text("1"))
)

contribution_hours = (
    session.query(
        func.date_trunc(
            "week", Interaction.created_at.op("AT TIME ZONE")(User.utc_locale)
        ).label("created_at"),
        func.avg(
            func.date_part(
                "hour", Interaction.created_at.op("AT TIME ZONE")(User.utc_locale)
            ).label("hours")
        ),
    )
    .join(User)
    .filter(User.utc_locale != "uninhabited")
    .group_by(text("1"))
)


# weekly_interactions_per_week = """
# SELECT date_trunc('week', i.created_at AT TIME ZONE u.utc_locale) as time,
#          COUNT(*) filter (where extract(isodow from i.created_at AT TIME ZONE u.utc_locale) IN (1, 2)) / COUNT(*)::float
# from interactions i
#          INNER JOIN users u on i.user_id = u.id
# WHERE u.utc_locale is not null
#   AND u.utc_locale not like 'uninhabited'
#   AND i.repository_id = '$project'
# GROUP BY 1
# ORDER BY 1
# """


def to_csv(data: List[Dict], filepath):
    keys = data[0].keys()
    with open(filepath, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def general_interactions(*args, **kwargs):
    base_query = interactions_per_week
    data = []
    for id, full_name in REPOS:
        query = base_query.filter(Repository.full_name == full_name)
        before = query.filter(Interaction.created_at < OUTBREAK).all()
        before = [data[1] for data in before]
        after = query.filter(Interaction.created_at > OUTBREAK).all()
        after = [data[1] for data in after]
        data.append(
            {
                "repository": full_name,
                "before": f"{mean(before):.2f}",
                "after": f"{mean(after):.2f}",
                "change": f"{1 -  mean(before) / mean(after):.2%}",
                "before_stdev": f"{stdev(before):.2f}",
                "after_stdev": f"{stdev(after):.2f}",
                "mann_whithney_pvalue": f"{mannwhitneyu(before, after)[1]:.5f}",
            }
        )
    to_csv(data, "output/interactions.csv")
    logger.info(f"Wrote '{len(data)}' lines into interactions.csv")


def weekday_contributions(*args, **kwargs):
    base_query = weekend_interactions_per_week
    data = []
    for id, full_name in REPOS:
        query = base_query.filter(Interaction.repository_id == id)
        before = query.filter(Interaction.created_at < OUTBREAK).all()
        before = [data[1] for data in before]
        after = query.filter(Interaction.created_at > OUTBREAK).all()
        after = [data[1] for data in after]
        data.append(
            {
                "repository": full_name,
                "before": f"{mean(before):.2%}",
                "after": f"{mean(after):.2%}",
                "change": f"{1 -  mean(before) / mean(after):.2%}",
                "before_stdev": f"{stdev(before):.2f}",
                "after_stdev": f"{stdev(after):.2f}",
                "mann_whithney_pvalue": f"{mannwhitneyu(before, after)[1]:.5f}",
            }
        )
    to_csv(data, "output/interactions_weekends.csv")
    logger.info(f"Wrote '{len(data)}' lines into interactions_weekends.csv")


def average_contribution_hours(*args, **kwargs):
    base_query = contribution_hours
    data = []
    for id, full_name in REPOS:
        query = base_query.filter(Interaction.repository_id == id)
        before = query.filter(Interaction.created_at < OUTBREAK).all()
        before = [data[1] for data in before]
        after = query.filter(Interaction.created_at > OUTBREAK).all()
        after = [data[1] for data in after]
        data.append(
            {
                "repository": full_name,
                "before": f"{mean(before):.2f}",
                "after": f"{mean(after):.2f}",
                "change": f"{1 -  mean(before) / mean(after):.2%}",
                "before_stdev": f"{stdev(before):.2f}",
                "after_stdev": f"{stdev(after):.2f}",
                "mann_whithney_pvalue": f"{mannwhitneyu(before, after)[1]:.5f}",
            }
        )
    to_csv(data, "output/interactions_hours.csv")
    logger.info(f"Wrote '{len(data)}' lines into hours.csv")
