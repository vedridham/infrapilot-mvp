from sqlalchemy import text


def get_recent_deployments(db, limit=5):
    """
    Read-only diagnostic tool.
    Returns the most recent deployment events.
    """
    result = db.execute(
        text(
            """
            SELECT id, service_name, version, change_summary, deployed_at
            FROM deployments
            ORDER BY deployed_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )

    return [dict(row._mapping) for row in result]


def get_top_slow_queries(db, limit=5):
    """
    Read-only diagnostic tool.
    Returns the slowest synthetic database query samples.
    """
    result = db.execute(
        text(
            """
            SELECT endpoint, db_query_latency_ms, api_latency_ms,
                   api_error_rate, db_cpu_percent, recorded_at
            FROM telemetry_samples
            WHERE telemetry_source = 'synthetic'
            ORDER BY db_query_latency_ms DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )

    return [dict(row._mapping) for row in result]
def get_query_plan(db):
    """
    Read-only diagnostic tool.
    Returns the execution plan for the known order-history query.
    """
    result = db.execute(
        text(
            """
            EXPLAIN
            SELECT *
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            """
        ),
        {"user_id": 1},
    )

    return [row[0] for row in result]