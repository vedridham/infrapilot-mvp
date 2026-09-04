from app.diagnostics import (
    get_recent_deployments,
    get_top_slow_queries,
    get_query_plan,
)


def investigate_incident(db):
    """
    Collects read-only evidence for an incident.
    """

    return {
        "deployments": get_recent_deployments(db),
        "slow_queries": get_top_slow_queries(db),
        "query_plan": get_query_plan(db),
    }