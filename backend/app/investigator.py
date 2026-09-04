from app.diagnostics import (
    get_recent_deployments,
    get_top_slow_queries,
    get_query_plan,
)
from app.ai_investigator import generate_diagnosis


def investigate_incident(db):
    """
    Collects read-only evidence and generates a diagnosis.
    """

    evidence = {
        "deployments": get_recent_deployments(db),
        "slow_queries": get_top_slow_queries(db),
        "query_plan": get_query_plan(db),
    }

    diagnosis = generate_diagnosis(evidence)

    return {
        "evidence": evidence,
        "diagnosis": diagnosis,
    }