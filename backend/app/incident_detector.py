import json
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


ORDER_HISTORY_ENDPOINT = "/api/orders/history/{user_id}"
P95_LATENCY_THRESHOLD_MS = 500
ERROR_RATE_THRESHOLD_PERCENT = 5


@dataclass
class DetectionResult:
    incident_id: int | None
    endpoint: str
    p95_latency_ms: float
    error_rate: float
    incident_created: bool


def detect_order_history_incident(db: Session) -> DetectionResult | None:
    metrics = db.execute(
        text(
            """
            SELECT
                percentile_cont(0.95)
                    WITHIN GROUP (ORDER BY api_latency_ms) AS p95_latency_ms,
                AVG(api_error_rate) AS average_error_rate
            FROM telemetry_samples
            WHERE endpoint = :endpoint
              AND telemetry_source = 'synthetic'
            """
        ),
        {"endpoint": ORDER_HISTORY_ENDPOINT},
    ).mappings().one()

    p95_latency_ms = float(metrics["p95_latency_ms"])
    error_rate = float(metrics["average_error_rate"])

    if (
        p95_latency_ms <= P95_LATENCY_THRESHOLD_MS
        or error_rate <= ERROR_RATE_THRESHOLD_PERCENT
    ):
        return DetectionResult(
            incident_id=None,
            endpoint=ORDER_HISTORY_ENDPOINT,
            p95_latency_ms=p95_latency_ms,
            error_rate=error_rate,
            incident_created=False,
        )

    existing_incident_id = db.execute(
        text(
            """
            SELECT id
            FROM incidents
            WHERE endpoint = :endpoint
              AND status IN ('open', 'investigating')
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"endpoint": ORDER_HISTORY_ENDPOINT},
    ).scalar_one_or_none()

    if existing_incident_id is not None:
        return DetectionResult(
            incident_id=existing_incident_id,
            endpoint=ORDER_HISTORY_ENDPOINT,
            p95_latency_ms=p95_latency_ms,
            error_rate=error_rate,
            incident_created=False,
        )

    evidence = {
        "telemetry_source": "synthetic",
        "detector": "p95_latency_and_error_rate_threshold",
        "p95_latency_ms": p95_latency_ms,
        "p95_threshold_ms": P95_LATENCY_THRESHOLD_MS,
        "error_rate_percent": error_rate,
        "error_rate_threshold_percent": ERROR_RATE_THRESHOLD_PERCENT,
    }

    incident_id = db.execute(
        text(
            """
            INSERT INTO incidents
            (
                status,
                severity,
                endpoint,
                started_at,
                p95_latency_ms,
                threshold_ms,
                error_rate,
                evidence
            )
            SELECT
                'open',
                'high',
                :incident_endpoint,
                MIN(recorded_at),
                :p95_latency_ms,
                :threshold_ms,
                :error_rate,
                CAST(:evidence AS JSONB)
            FROM telemetry_samples
            WHERE endpoint = :telemetry_endpoint
              AND telemetry_source = 'synthetic'
            RETURNING id
            """
        ),
        {
            "incident_endpoint": ORDER_HISTORY_ENDPOINT,
	    "telemetry_endpoint": ORDER_HISTORY_ENDPOINT,
            "p95_latency_ms": p95_latency_ms,
            "threshold_ms": P95_LATENCY_THRESHOLD_MS,
            "error_rate": error_rate,
            "evidence": json.dumps(evidence),
        },
    ).scalar_one()

    db.commit()

    return DetectionResult(
        incident_id=incident_id,
        endpoint=ORDER_HISTORY_ENDPOINT,
        p95_latency_ms=p95_latency_ms,
        error_rate=error_rate,
        incident_created=True,
    )