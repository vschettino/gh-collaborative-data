from .interactions import (
    average_contribution_hours,
    general_interactions,
    weekday_contributions,
)

OPTIONS = {
    "interactions": general_interactions,
    "weekday_contributions": weekday_contributions,
    "average_contribution_hours": average_contribution_hours,
}
