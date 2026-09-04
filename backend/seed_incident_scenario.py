import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.database import engine


ENDPOINT = "/api/orders/history/{user_id}"
HEALTHY_SAMPLE_COUNT = 30
DEGRADED_SAMPLE_COUNT = 30

random.seed(42)


def main() -> None:
    with engine.begin() as connection:
        existing_sample_count = connection.execute(
            text("SELECT COUNT(*) FROM telemetry_samples")
        ).scalar_one()

        if existing_sample_count > 0:
            raise SystemExit(
                "Telemetry already exists. Refusing to create a duplicate scenario."
            )

        now = datetime.now(timezone.utc)
        deployment_time = now - timedelta(minutes=DEGRADED_SAMPLE_COUNT)

        connection.execute(
            text(
                """
                INSERT INTO deployments
                (service_name, version, change_summary, deployed_at, telemetry_source)
                VALUES
                (:service_name, :version, :change_summary, :deployed_at, 'synthetic')
                """
            ),
            {
                "service_name": "orders-api",
                "version": "demo-order-history-release",
                "change_summary": (
                    "Released order-history lookup without a usable "
                    "orders(user_id, created_at) index."
                ),
                "deployed_at": deployment_time,
            },
        )

        healthy_samples = [
            {
                "recorded_at": now - timedelta(minutes=60 - minute),
                "endpoint": ENDPOINT,
                "api_latency_ms": round(random.uniform(90, 150), 2),
                "db_query_latency_ms": round(random.uniform(20, 50), 2),
                "api_error_rate": round(random.uniform(0, 1), 2),
                "db_cpu_percent": round(random.uniform(20, 35), 2),
            }
            for minute in range(HEALTHY_SAMPLE_COUNT)
        ]

        degraded_samples = [
            {
                "recorded_at": deployment_time + timedelta(minutes=minute),
                "endpoint": ENDPOINT,
                "api_latency_ms": round(random.uniform(850, 1_250), 2),
                "db_query_latency_ms": round(random.uniform(650, 950), 2),
                "api_error_rate": round(random.uniform(8, 18), 2),
                "db_cpu_percent": round(random.uniform(75, 92), 2),
            }
            for minute in range(DEGRADED_SAMPLE_COUNT)
        ]

        connection.execute(
            text(
                """
                INSERT INTO telemetry_samples
                (
                    recorded_at,
                    endpoint,
                    api_latency_ms,
                    db_query_latency_ms,
                    api_error_rate,
                    db_cpu_percent,
                    telemetry_source
                )
                VALUES
                (
                    :recorded_at,
                    :endpoint,
                    :api_latency_ms,
                    :db_query_latency_ms,
                    :api_error_rate,
                    :db_cpu_percent,
                    'synthetic'
                )
                """
            ),
            healthy_samples + degraded_samples,
        )

    print(
        "Created one synthetic deployment and "
        f"{HEALTHY_SAMPLE_COUNT + DEGRADED_SAMPLE_COUNT} telemetry samples."
    )


if __name__ == "__main__":
    main()