import logging

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
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
    by_project = df.groupby(["project", "created_at"]).sum("total")
    plt.figure(figsize=(15, 8))

    plot = sns.relplot(
        data=by_project, x="created_at", y="total", kind="line", hue="project"
    )
    plt.gcf().set_size_inches(11.7, 8.27)
    plot.savefig("output/iter_by_project.png")
