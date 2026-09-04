def generate_diagnosis(evidence):
    """
    Creates a deterministic incident diagnosis from collected evidence.
    """

    slow_queries = evidence.get("slow_queries", [])
    query_plan = evidence.get("query_plan", [])
    deployments = evidence.get("deployments", [])

    diagnosis = {
        "probable_cause": "Unknown",
        "confidence": "low",
        "evidence": [],
        "blast_radius": "Unknown",
        "remediation": "Investigate the affected endpoint and database query.",
        "rollback_plan": "Review the latest deployment before taking action.",
    }

    if slow_queries:
        top_query = slow_queries[0]

        diagnosis["evidence"].append(
            {
                "type": "FACT",
                "source": "slow_queries",
                "detail": (
                    f"Highest observed DB query latency: "
                    f"{top_query['db_query_latency_ms']} ms "
                    f"for {top_query['endpoint']}"
                ),
            }
        )

        if top_query["db_cpu_percent"] >= 80:
            diagnosis["evidence"].append(
                {
                    "type": "FACT",
                    "source": "telemetry",
                    "detail": (
                        f"Database CPU reached "
                        f"{top_query['db_cpu_percent']}%"
                    ),
                }
            )

    if query_plan:
        seq_scan_found = any("Seq Scan" in line for line in query_plan)

        if seq_scan_found:
            diagnosis["probable_cause"] = (
                "Database sequential scan is contributing to "
                "high query latency."
            )
            diagnosis["confidence"] = "high"

            diagnosis["evidence"].append(
                {
                    "type": "FACT",
                    "source": "query_plan",
                    "detail": "EXPLAIN output contains a sequential scan on orders.",
                }
            )

    if deployments:
        latest = deployments[0]

        diagnosis["evidence"].append(
            {
                "type": "FACT",
                "source": "deployment",
                "detail": (
                    f"Latest deployment: {latest['version']} "
                    f"({latest['change_summary']})"
                ),
            }
        )

        if diagnosis["probable_cause"] != "Unknown":
            diagnosis["blast_radius"] = (
                "The affected order-history endpoint and requests "
                "depending on this database query."
            )

            diagnosis["remediation"] = (
                "Validate the missing/ineffective index in staging, "
                "then consider rolling back the deployment if production "
                "impact is ongoing."
            )

            diagnosis["rollback_plan"] = (
                f"Consider rolling back {latest['version']} "
                "after human approval."
            )

    return diagnosis