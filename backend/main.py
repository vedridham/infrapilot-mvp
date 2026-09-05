import json
from typing import Annotated

from fastapi import Depends, FastAPI, Path, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.order_history import get_order_history
from app.diagnostics import (
    get_recent_deployments,
    get_top_slow_queries,
    get_query_plan,
)
from app.investigator import investigate_incident


app = FastAPI(
    title="InfraPilot API",
    version="0.1.0",
)


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/orders/history/{user_id}")
def order_history(
    user_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_order_history(db, user_id)


@app.get("/api/diagnostics/deployments")
def recent_deployments(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_recent_deployments(db)


@app.get("/api/diagnostics/slow-queries")
def top_slow_queries(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_top_slow_queries(db)


@app.get("/api/diagnostics/query-plan")
def query_plan(
    db: Annotated[Session, Depends(get_db)],
) -> list[str]:
    return get_query_plan(db)


@app.get("/api/investigate")
def investigate(
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return investigate_incident(db)


@app.post("/api/incidents/{incident_id}/approve")
def approve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.execute(
        text("SELECT id FROM incidents WHERE id = :incident_id"),
        {"incident_id": incident_id},
    ).fetchone()

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    result = db.execute(
        text(
            """
            INSERT INTO audit_logs (incident_id, action, actor, details)
            VALUES (
                :incident_id,
                'APPROVED',
                'developer',
                :details
            )
            RETURNING id, incident_id, action, actor, details, created_at
            """
        ),
        {
            "incident_id": incident_id,
            "details": json.dumps({"source": "infrapilot-ui"}),
        },
    )

    db.commit()

    return dict(result.fetchone()._mapping)


@app.post("/api/incidents/{incident_id}/reject")
def reject_incident(
    incident_id: int,
    request: RejectRequest,
    db: Session = Depends(get_db),
):
    incident = db.execute(
        text("SELECT id FROM incidents WHERE id = :incident_id"),
        {"incident_id": incident_id},
    ).fetchone()

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    result = db.execute(
        text(
            """
            INSERT INTO audit_logs (incident_id, action, actor, details)
            VALUES (
                :incident_id,
                'REJECTED',
                'developer',
                :details
            )
            RETURNING id, incident_id, action, actor, details, created_at
            """
        ),
        {
            "incident_id": incident_id,
            "details": json.dumps({"reason": request.reason}),
        },
    )

    db.commit()

    return dict(result.fetchone()._mapping)


@app.get("/api/incidents/{incident_id}/audit-logs")
def get_incident_audit_logs(
    incident_id: int,
    db: Session = Depends(get_db),
):
    result = db.execute(
        text(
            """
            SELECT id, incident_id, action, actor, details, created_at
            FROM audit_logs
            WHERE incident_id = :incident_id
            ORDER BY created_at DESC
            """
        ),
        {"incident_id": incident_id},
    )

    return [dict(row._mapping) for row in result]